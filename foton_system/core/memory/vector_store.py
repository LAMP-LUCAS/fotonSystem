"""
VectorStore - Memória Semântica do FOTON System

Armazena e consulta documentos usando embeddings vetoriais (ChromaDB).
Modelo: paraphrase-multilingual-MiniLM-L12-v2 (otimizado para PT-BR).

DESIGN NOTES:
- Singleton para evitar múltiplas instâncias do modelo em memória
- Graceful degradation: falha na inicialização é logada mas não impede o sistema
- Persistência local em %LOCALAPPDATA%/FotonSystem/memory_db
- Circuit breaker: após 3 falhas consecutivas no ChromaDB, entra em OPEN por 60s
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

# Modelo otimizado para português brasileiro
EMBEDDING_MODEL = 'paraphrase-multilingual-MiniLM-L12-v2'
COLLECTION_NAME = 'foton_knowledge_base'


class CircuitBreakerOpenError(RuntimeError):
    """Raised when the circuit breaker is OPEN and refuses a call."""


class CircuitBreaker:
    """
    Circuit breaker for external service calls (e.g. ChromaDB).

    States:
        CLOSED  — normal operation, calls pass through
        OPEN    — failures exceeded threshold, calls are refused
        HALF_OPEN — after timeout, one probe call is allowed

    Threshold: 3 consecutive failures → OPEN
    Recovery:  60s in OPEN → HALF_OPEN → 1 probe → CLOSED or back to OPEN
    """

    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 60.0):
        self._state = "CLOSED"
        self._failure_count = 0
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._last_failure_time = 0.0
        self._last_exception: Optional[str] = None

    @property
    def state(self) -> str:
        return self._state

    @property
    def last_exception(self) -> Optional[str]:
        return self._last_exception

    def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        if self._state == "OPEN":
            if time.time() - self._last_failure_time >= self._recovery_timeout:
                self._state = "HALF_OPEN"
                logger.info("Circuit breaker HALF_OPEN — allowing probe call")
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN (retry in {self._recovery_timeout - (time.time() - self._last_failure_time):.0f}s)"
                )

        try:
            result = func(*args, **kwargs)
            self._last_exception = None
            if self._state == "HALF_OPEN":
                self._state = "CLOSED"
                self._failure_count = 0
                self._last_failure_time = 0.0
                logger.info("Circuit breaker CLOSED — probe call succeeded")
            return result
        except Exception as e:
            self._failure_count += 1
            self._last_exception = f"{type(e).__name__}: {e}"
            if self._state == "HALF_OPEN" or self._failure_count >= self._failure_threshold:
                self._state = "OPEN"
                self._last_failure_time = time.time()
                logger.warning(
                    f"Circuit breaker OPEN after {self._failure_count} failures "
                    f"(next retry in {self._recovery_timeout:.0f}s): {self._last_exception}"
                )
            raise


class VectorStore:
    """Banco vetorial para busca semântica nos documentos do escritório."""

    _instance: Optional['VectorStore'] = None

    def __new__(cls) -> 'VectorStore':
        if cls._instance is None:
            cls._instance = super(VectorStore, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialize()

    def _initialize(self) -> None:
        """Inicializa ChromaDB e modelo de embeddings."""
        from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService

        try:
            self._try_import_packages()
        except ImportError:
            self._try_install_ai_pack()
            self._try_import_packages()

        try:
            import chromadb
            from sentence_transformers import SentenceTransformer

            config_dir = BootstrapService.get_user_config_dir()
            self.db_path: Path = config_dir / "memory_db"
            self.db_path.mkdir(parents=True, exist_ok=True)

            logging.getLogger("chromadb").setLevel(logging.ERROR)

            self.client = chromadb.PersistentClient(path=str(self.db_path))

            logger.info(f"Carregando modelo de embeddings: {EMBEDDING_MODEL}")
            self.embedder = SentenceTransformer(EMBEDDING_MODEL)

            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )

            self._breaker = CircuitBreaker()
            self._initialized = True
            logger.info(f"VectorStore inicializado em {self.db_path}")

        except ImportError as e:
            logger.error(f"Dependência RAG faltando: {e}")
            raise
        except Exception as e:
            logger.error(f"Falha ao inicializar VectorStore: {e}")
            raise

    def _try_import_packages(self) -> None:
        """Tenta importar chromadb e sentence_transformers (global, VENV, ou fallback)."""
        from foton_system.infrastructure.dependency_manager import DependencyManager

        tried = []

        # Try global site-packages FIRST (clean, no VENV interference)
        for base in (sys.base_exec_prefix, sys.exec_prefix):
            site_pkgs = Path(base) / "Lib" / "site-packages"
            if site_pkgs.exists() and str(site_pkgs) not in sys.path:
                sys.path.insert(0, str(site_pkgs))
                tried.append(f"system:{site_pkgs}")

        for ver in ("Python312", "Python313", "Python311"):
            for base in (Path(os.environ.get("LOCALAPPDATA", "C:\\Users\\Default")) / "Programs" / "Python",
                         Path("C:\\Program Files") / "Python",
                         Path("C:\\Python")):
                site_pkgs = base / ver / "Lib" / "site-packages"
                if site_pkgs.exists() and str(site_pkgs) not in sys.path:
                    sys.path.insert(0, str(site_pkgs))
                    tried.append(f"common:{site_pkgs}")

        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
            return
        except Exception:
            pass

        # Fallback: VENV site-packages (last resort, might have broken torch)
        ai_path = DependencyManager.get_plugin_python_path("ai_pack")
        if ai_path and str(ai_path) not in sys.path:
            sys.path.insert(0, str(ai_path))
            tried.append(f"venv:{ai_path}")

        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
            return
        except Exception:
            pass

        raise ImportError(
            f"Não foi possível importar chromadb/sentence_transformers. "
            f"Caminhos tentados: {tried}"
        )

    def _try_install_ai_pack(self) -> None:
        """Tenta instalar o AI Pack interativamente (CLI) ou aborta (MCP)."""
        from foton_system.infrastructure.dependency_manager import DependencyManager

        AI_PACK_PACKAGES = ["chromadb", "sentence-transformers", "torch", "transformers"]

        if "--mcp" in sys.argv:
            raise RuntimeError(
                "Módulo de Memória Semântica (IA) não instalado. "
                "Execute o Foton em modo CLI e escolha 's' para instalar "
                "o AI Pack (~800MB) quando solicitado."
            )

        print("\n🤖 O módulo de Memória Semântica (IA) não está instalado.")
        choice = input("👉 Deseja instalar o AI Pack agora? (~800MB) [s/N]: ")
        if choice.lower() != 's':
            logger.info("Usuário optou por não instalar o AI Pack.")
            raise ImportError("AI Pack não instalado.")

        extra_args = None
        if sys.platform == "win32":
            extra_args = ["--extra-index-url", "https://download.pytorch.org/whl/cu118"]
        if not DependencyManager.install_plugin("ai_pack", AI_PACK_PACKAGES, extra_args):
            raise RuntimeError("Falha ao instalar pacotes de IA.")

    def _do_add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """Actual ChromaDB upsert (unprotected)."""
        embeddings = self.embedder.encode(documents).tolist()
        self.collection.upsert(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def _do_query(self, query_text: str, n_results: int = 5, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Actual ChromaDB query (unprotected). Supports optional metadata filter."""
        query_embedding = self.embedder.encode([query_text]).tolist()
        kwargs: Dict[str, Any] = {
            "query_embeddings": query_embedding,
            "n_results": n_results
        }
        if where:
            kwargs["where"] = where
        return self.collection.query(**kwargs)

    def _do_delete(self, ids: List[str]) -> None:
        """Actual ChromaDB delete (unprotected)."""
        self.collection.delete(ids=ids)

    def _do_count(self) -> int:
        """Actual ChromaDB count (unprotected)."""
        return self.collection.count()

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """
        Gera embeddings e insere/atualiza documentos no banco vetorial.
        Protegido por circuit breaker — retorna silenciosamente se indisponível.

        Args:
            documents: Lista de textos a serem indexados
            metadatas: Lista de metadados associados a cada documento
            ids: Lista de IDs únicos para cada documento
        """
        if not documents:
            return
        try:
            self._breaker.call(self._do_add_documents, documents, metadatas, ids)
        except CircuitBreakerOpenError:
            logger.warning("add_documents skipped — ChromaDB unavailable (circuit OPEN)")

    def query(self, query_text: str, n_results: int = 5, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Busca semântica na base de conhecimento.
        Protegido por circuit breaker — retorna vazio se indisponível.

        Args:
            query_text: Pergunta ou termo de busca em linguagem natural
            n_results: Quantidade máxima de resultados
            where: Filtro opcional de metadados (ex: {"source": {"$contains": "ClienteX"}})

        Returns:
            Dicionário com 'documents', 'metadatas', 'distances' e 'ids'
        """
        try:
            return self._breaker.call(self._do_query, query_text, n_results, where)
        except CircuitBreakerOpenError:
            logger.warning("query skipped — ChromaDB unavailable (circuit OPEN)")
            return {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
                "ids": [[]]
            }

    def delete(self, ids: List[str]) -> None:
        """Remove documentos do banco vetorial pelos seus IDs."""
        try:
            self._breaker.call(self._do_delete, ids)
        except CircuitBreakerOpenError:
            logger.warning("delete skipped — ChromaDB unavailable (circuit OPEN)")

    def count(self) -> int:
        """Retorna a quantidade de documentos indexados."""
        try:
            return self._breaker.call(self._do_count)
        except CircuitBreakerOpenError:
            logger.warning("count skipped — ChromaDB unavailable (circuit OPEN)")
            return 0

    def diagnostic(self) -> Dict[str, Any]:
        """
        Retorna diagnóstico completo da base de conhecimento.

        Returns:
            Dicionário com:
                - total_chunks: Quantidade de chunks indexados
                - circuit_breaker_status: "CLOSED" | "OPEN" | "HALF_OPEN"
                - ultima_indexacao: Timestamp ISO da última indexação ou "N/A"
        """
        total = self.count()
        cb_state = self._breaker.state
        last_idx = "N/A"
        index_marker = self.db_path / ".last_indexed"
        if index_marker.exists():
            try:
                last_idx = index_marker.read_text(encoding="utf-8").strip()
            except Exception:
                pass
        return {
            "total_chunks": total,
            "circuit_breaker_status": cb_state,
            "ultima_indexacao": last_idx
        }

    @staticmethod
    def mark_indexed() -> None:
        """Marca o timestamp atual como última indexação."""
        from datetime import datetime
        try:
            from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService
            config_dir = BootstrapService.get_user_config_dir()
            marker = config_dir / "memory_db" / ".last_indexed"
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), encoding="utf-8")
        except Exception:
            pass


class VectorStoreInstance:
    """Instância única de armazenamento vetorial para um modelo específico.

    Cada instância gerencia seu próprio embedder, collection ChromaDB e circuit breaker.
    A collection é nomeada como foton_{model_tag}_{dimensions}d.
    """

    def __init__(self, model_tag: str, model_entry, config_dir: Path) -> None:
        self.model_tag = model_tag
        self.model_entry = model_entry
        self.config_dir = config_dir
        self.db_path: Path = config_dir / "memory_db"
        self.db_path.mkdir(parents=True, exist_ok=True)
        self._initialized = False
        self._initialize()

    def _try_import_packages(self) -> None:
        """Tenta importar chromadb e sentence_transformers."""
        from foton_system.infrastructure.dependency_manager import DependencyManager

        tried = []

        for base in (sys.base_exec_prefix, sys.exec_prefix):
            site_pkgs = Path(base) / "Lib" / "site-packages"
            if site_pkgs.exists() and str(site_pkgs) not in sys.path:
                sys.path.insert(0, str(site_pkgs))
                tried.append(f"system:{site_pkgs}")

        for ver in ("Python312", "Python313", "Python311"):
            for base in (Path(os.environ.get("LOCALAPPDATA", "C:\\Users\\Default")) / "Programs" / "Python",
                         Path("C:\\Program Files") / "Python",
                         Path("C:\\Python")):
                site_pkgs = base / ver / "Lib" / "site-packages"
                if site_pkgs.exists() and str(site_pkgs) not in sys.path:
                    sys.path.insert(0, str(site_pkgs))
                    tried.append(f"common:{site_pkgs}")

        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
            return
        except Exception:
            pass

        ai_path = DependencyManager.get_plugin_python_path("ai_pack")
        if ai_path and str(ai_path) not in sys.path:
            sys.path.insert(0, str(ai_path))
            tried.append(f"venv:{ai_path}")

        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
            return
        except Exception:
            pass

        raise ImportError(
            f"Não foi possível importar chromadb/sentence_transformers. "
            f"Caminhos tentados: {tried}"
        )

    def _initialize(self) -> None:
        from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService

        try:
            self._try_import_packages()
        except ImportError:
            from foton_system.core.memory.vector_store import VectorStore
            VectorStore._try_install_ai_pack()
            self._try_import_packages()

        try:
            import chromadb
            from sentence_transformers import SentenceTransformer

            logging.getLogger("chromadb").setLevel(logging.ERROR)

            self.client = chromadb.PersistentClient(path=str(self.db_path))

            model_name = self.model_entry.name
            dims = self.model_entry.dimensions
            self.collection_name = f"foton_{self.model_tag}_{dims}d"

            logger.info("Carregando modelo de embeddings: %s (tag=%s)", model_name, self.model_tag)
            self.embedder = SentenceTransformer(model_name)

            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "hnsw:space": "cosine",
                    "model_name": model_name,
                    "model_tag": self.model_tag,
                    "dimensions": str(dims),
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                },
            )

            self._breaker = CircuitBreaker()
            self._initialized = True
            logger.info(
                "VectorStoreInstance '%s' inicializada (collection=%s)",
                self.model_tag, self.collection_name,
            )

        except ImportError as e:
            logger.error("Dependência RAG faltando para '%s': %s", self.model_tag, e)
            raise
        except Exception as e:
            logger.error("Falha ao inicializar VectorStoreInstance '%s': %s", self.model_tag, e)
            raise

    def _do_add_documents(
        self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]
    ) -> None:
        embeddings = self.embedder.encode(documents).tolist()
        self.collection.upsert(
            embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids
        )

    def _do_query(
        self, query_text: str, n_results: int = 5, where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        query_embedding = self.embedder.encode([query_text]).tolist()
        kwargs: Dict[str, Any] = {"query_embeddings": query_embedding, "n_results": n_results}
        if where:
            kwargs["where"] = where
        return self.collection.query(**kwargs)

    def _do_delete(self, ids: List[str]) -> None:
        self.collection.delete(ids=ids)

    def _do_count(self) -> int:
        return self.collection.count()

    def add_documents(
        self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]
    ) -> None:
        if not documents:
            return
        try:
            self._breaker.call(self._do_add_documents, documents, metadatas, ids)
        except CircuitBreakerOpenError:
            logger.warning(
                "add_documents (%s) skipped — ChromaDB unavailable (circuit OPEN)", self.model_tag
            )

    def embed_query(self, text: str) -> List[float]:
        try:
            return self._breaker.call(self._do_embed_query, text)
        except CircuitBreakerOpenError:
            logger.warning("embed_query (%s) skipped — ChromaDB unavailable (circuit OPEN)", self.model_tag)
            return []

    def _do_embed_query(self, text: str) -> List[float]:
        return self.embedder.encode([text]).tolist()[0]

    def query_with_embeddings(
        self, embeddings: List[float], n_results: int = 5, where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        try:
            return self._breaker.call(self._do_query_with_embeddings, embeddings, n_results, where)
        except CircuitBreakerOpenError:
            logger.warning("query_with_embeddings (%s) skipped — ChromaDB unavailable (circuit OPEN)", self.model_tag)
            return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}

    def _do_query_with_embeddings(
        self, embeddings: List[float], n_results: int = 5, where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"query_embeddings": [embeddings], "n_results": n_results}
        if where:
            kwargs["where"] = where
        return self.collection.query(**kwargs)

    def query(
        self, query_text: str, n_results: int = 5, where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        try:
            return self._breaker.call(self._do_query, query_text, n_results, where)
        except CircuitBreakerOpenError:
            logger.warning("query (%s) skipped — ChromaDB unavailable (circuit OPEN)", self.model_tag)
            return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}

    def delete(self, ids: List[str]) -> None:
        try:
            self._breaker.call(self._do_delete, ids)
        except CircuitBreakerOpenError:
            logger.warning("delete (%s) skipped — ChromaDB unavailable (circuit OPEN)", self.model_tag)

    def count(self) -> int:
        try:
            return self._breaker.call(self._do_count)
        except CircuitBreakerOpenError:
            logger.warning("count (%s) skipped — ChromaDB unavailable (circuit OPEN)", self.model_tag)
            return 0

    def diagnostic(self) -> Dict[str, Any]:
        total = self.count()
        cb_state = self._breaker.state
        last_idx = "N/A"
        index_marker = self.db_path / ".last_indexed"
        if index_marker.exists():
            try:
                last_idx = index_marker.read_text(encoding="utf-8").strip()
            except Exception:
                pass
        return {
            "model_tag": self.model_tag,
            "model_name": self.model_entry.name,
            "collection_name": self.collection_name,
            "dimensions": self.model_entry.dimensions,
            "total_chunks": total,
            "circuit_breaker_status": cb_state,
            "ultima_indexacao": last_idx,
        }


class VectorStoreManager:
    """Facade singleton que gerencia N instâncias de VectorStoreInstance.

    Substitui o VectorStore original para operações multi-modelo.
    Backward compat (RAG-10.7): sem config 'rag', opera em modo minilm.
    """

    _instance: Optional['VectorStoreManager'] = None

    def __new__(cls) -> 'VectorStoreManager':
        if cls._instance is None:
            cls._instance = super(VectorStoreManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._instances: Dict[str, VectorStoreInstance] = {}
        self._active_tags: List[str] = []
        self._config_dir: Optional[Path] = None
        self._mode: str = "minilm"
        self._initialized = True
        self._lazy_init_done = False

    def _ensure_config_dir(self) -> Path:
        if self._config_dir is None:
            from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService
            self._config_dir = BootstrapService.get_user_config_dir()
        return self._config_dir

    def _lazy_init(self) -> None:
        if self._lazy_init_done:
            return
        self._lazy_init_done = True

        try:
            from foton_system.core.rag.migration import MigrationChecker
            MigrationChecker().ensure_migrated()

            from foton_system.modules.shared.infrastructure.config.config import Config
            config = Config()
            rag_cfg = config.rag_config

            from foton_system.core.rag.model_registry import ModelRegistry
            from foton_system.core.rag.hardware_profiler import HardwareProfiler
            from foton_system.core.rag.model_router import ModelRouter

            registry = ModelRegistry()
            profiler = HardwareProfiler()
            hardware = profiler.detect()

            self._mode = rag_cfg.get("mode", "minilm")
            active = ModelRouter.resolve(config=config._settings, hardware=hardware, registry=registry)

            warnings = ModelRouter.validate_pipeline_feasibility(
                config=config._settings, hardware=hardware
            )
            for w in warnings:
                logger.warning("Pipeline feasibility: %s", w)

            self._active_tags = active
            config_dir = self._ensure_config_dir()

            for tag in active:
                entry = registry.get(tag)
                if entry and tag not in self._instances:
                    try:
                        instance = VectorStoreInstance(tag, entry, config_dir)
                        self._instances[tag] = instance
                    except Exception as e:
                        logger.error(
                            "Falha ao criar VectorStoreInstance '%s': %s", tag, e
                        )

        except Exception as e:
            logger.warning("Falha lazy_init VectorStoreManager: %s. Fallback minilm.", e)
            self._mode = "minilm"
            self._active_tags = ["minilm"]
            if "minilm" not in self._instances:
                try:
                    from foton_system.core.rag.model_registry import ModelRegistry, ModelEntry
                    registry = ModelRegistry()
                    entry = registry.get("minilm") or ModelEntry(
                        id="minilm",
                        name="paraphrase-multilingual-MiniLM-L12-v2",
                        type="embedding",
                        dimensions=384,
                        ram_required_gb=1.0,
                        disk_required_gb=0.5,
                        requires_gpu=False,
                        is_default=True,
                    )
                    instance = VectorStoreInstance("minilm", entry, self._ensure_config_dir())
                    self._instances["minilm"] = instance
                except Exception as e2:
                    logger.error("Falha fallback minilm VectorStoreManager: %s", e2)

    @property
    def active_tags(self) -> List[str]:
        self._lazy_init()
        return self._active_tags

    def get_instance(self, tag: str) -> Optional[VectorStoreInstance]:
        self._lazy_init()
        return self._instances.get(tag)

    def add_documents(
        self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]
    ) -> None:
        if not documents:
            return
        self._lazy_init()
        from foton_system.core.rag.model_router import ModelRouter
        for tag in self._active_tags:
            instance = self._instances.get(tag)
            if instance:
                try:
                    instance.add_documents(documents, metadatas, ids)
                except Exception as e:
                    logger.error("Erro ao indexar em '%s': %s", tag, e)
                    fallback = ModelRouter.runtime_fallback(tag, self._active_tags)
                    if fallback and fallback != tag:
                        logger.info("Runtime fallback '%s' -> '%s' para add_documents", tag, fallback)

    def query_with_embeddings(
        self, embeddings_dict: Dict[str, List[float]], n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        self._lazy_init()

        if len(self._active_tags) == 1:
            tag = self._active_tags[0]
            instance = self._instances.get(tag)
            if instance and tag in embeddings_dict:
                return instance.query_with_embeddings(embeddings_dict[tag], n_results, where)
            if instance:
                return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}
            return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}

        from foton_system.core.rag.model_router import ModelRouter
        all_results: List[Dict[str, Any]] = []
        for tag in self._active_tags:
            instance = self._instances.get(tag)
            if not instance or tag not in embeddings_dict:
                continue
            try:
                result = instance.query_with_embeddings(embeddings_dict[tag], n_results, where)
                docs = result.get("documents", [[]])[0]
                metas = result.get("metadatas", [[]])[0]
                dists = result.get("distances", [[]])[0]
                ids_list = result.get("ids", [[]])[0]
                for d, m, dist, rid in zip(docs, metas, dists, ids_list):
                    all_results.append({
                        "document": d,
                        "metadata": m,
                        "distance": dist,
                        "id": rid,
                        "_tag": tag,
                    })
            except Exception as e:
                logger.error("Erro query_with_embeddings em '%s': %s", tag, e)
                fallback_tag = ModelRouter.runtime_fallback(tag, self._active_tags)
                if fallback_tag:
                    fb_instance = self._instances.get(fallback_tag)
                    if fb_instance and fallback_tag in embeddings_dict:
                        try:
                            result = fb_instance.query_with_embeddings(
                                embeddings_dict[fallback_tag], n_results, where
                            )
                            docs = result.get("documents", [[]])[0]
                            metas = result.get("metadatas", [[]])[0]
                            dists = result.get("distances", [[]])[0]
                            ids_list = result.get("ids", [[]])[0]
                            for d, m, dist, rid in zip(docs, metas, dists, ids_list):
                                all_results.append({
                                    "document": d,
                                    "metadata": m,
                                    "distance": dist,
                                    "id": rid,
                                    "_tag": fallback_tag,
                                })
                        except Exception:
                            pass

        seen_ids = set()
        merged = []
        for r in sorted(all_results, key=lambda x: x["distance"]):
            rid = r["id"]
            if rid not in seen_ids:
                seen_ids.add(rid)
                merged.append(r)

        merged = merged[:n_results]

        return {
            "documents": [[r["document"] for r in merged]],
            "metadatas": [[r["metadata"] for r in merged]],
            "distances": [[r["distance"] for r in merged]],
            "ids": [[r["id"] for r in merged]],
        }

    def query(
        self, query_text: str, n_results: int = 5, where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        self._lazy_init()

        if len(self._active_tags) == 1:
            instance = self._instances.get(self._active_tags[0])
            if instance:
                return instance.query(query_text, n_results, where)
            return {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}

        from foton_system.core.rag.model_router import ModelRouter
        all_results: List[Dict[str, Any]] = []
        for tag in self._active_tags:
            instance = self._instances.get(tag)
            if not instance:
                continue
            try:
                result = instance.query(query_text, n_results, where)
                docs = result.get("documents", [[]])[0]
                metas = result.get("metadatas", [[]])[0]
                dists = result.get("distances", [[]])[0]
                ids_list = result.get("ids", [[]])[0]
                for d, m, dist, rid in zip(docs, metas, dists, ids_list):
                    all_results.append({
                        "document": d,
                        "metadata": m,
                        "distance": dist,
                        "id": rid,
                        "_tag": tag,
                    })
            except Exception as e:
                logger.error("Erro query em '%s': %s", tag, e)
                fallback_tag = ModelRouter.runtime_fallback(tag, self._active_tags)
                if fallback_tag:
                    fb_instance = self._instances.get(fallback_tag)
                    if fb_instance:
                        try:
                            result = fb_instance.query(query_text, n_results, where)
                            docs = result.get("documents", [[]])[0]
                            metas = result.get("metadatas", [[]])[0]
                            dists = result.get("distances", [[]])[0]
                            ids_list = result.get("ids", [[]])[0]
                            for d, m, dist, rid in zip(docs, metas, dists, ids_list):
                                all_results.append({
                                    "document": d,
                                    "metadata": m,
                                    "distance": dist,
                                    "id": rid,
                                    "_tag": fallback_tag,
                                })
                        except Exception:
                            pass

        seen_ids = set()
        merged = []
        for r in sorted(all_results, key=lambda x: x["distance"]):
            rid = r["id"]
            if rid not in seen_ids:
                seen_ids.add(rid)
                merged.append(r)

        merged = merged[:n_results]

        return {
            "documents": [[r["document"] for r in merged]],
            "metadatas": [[r["metadata"] for r in merged]],
            "distances": [[r["distance"] for r in merged]],
            "ids": [[r["id"] for r in merged]],
        }

    def delete(self, ids: List[str]) -> None:
        self._lazy_init()
        for tag in self._active_tags:
            instance = self._instances.get(tag)
            if instance:
                try:
                    instance.delete(ids)
                except Exception as e:
                    logger.error("Erro delete em '%s': %s", tag, e)

    def count(self) -> int:
        self._lazy_init()
        total = 0
        for tag in self._active_tags:
            instance = self._instances.get(tag)
            if instance:
                total += instance.count()
        return total

    def diagnostic(self) -> Dict[str, Any]:
        self._lazy_init()
        stores_diag = {}
        for tag in self._active_tags:
            instance = self._instances.get(tag)
            if instance:
                stores_diag[tag] = instance.diagnostic()
        return {
            "mode": self._mode,
            "stores": stores_diag,
        }

    @staticmethod
    def mark_indexed() -> None:
        VectorStore.mark_indexed()
