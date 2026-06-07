"""
VectorStore - Memória Semântica do FOTON System

Armazena e consulta documentos usando embeddings vetoriais (ChromaDB).
Modelo: paraphrase-multilingual-MiniLM-L12-v2 (otimizado para PT-BR).

DESIGN NOTES:
- Singleton para evitar múltiplas instâncias do modelo em memória
- Graceful degradation: falha na inicialização é logada mas não impede o sistema
- Persistência local em %LOCALAPPDATA%/FotonSystem/memory_db
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Modelo otimizado para português brasileiro
EMBEDDING_MODEL = 'paraphrase-multilingual-MiniLM-L12-v2'
COLLECTION_NAME = 'foton_knowledge_base'


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

        if not DependencyManager.install_plugin("ai_pack", AI_PACK_PACKAGES):
            raise RuntimeError("Falha ao instalar pacotes de IA.")

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """
        Gera embeddings e insere/atualiza documentos no banco vetorial.

        Args:
            documents: Lista de textos a serem indexados
            metadatas: Lista de metadados associados a cada documento
            ids: Lista de IDs únicos para cada documento
        """
        if not documents:
            return

        embeddings = self.embedder.encode(documents).tolist()

        self.collection.upsert(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Busca semântica na base de conhecimento.

        Args:
            query_text: Pergunta ou termo de busca em linguagem natural
            n_results: Quantidade máxima de resultados

        Returns:
            Dicionário com 'documents', 'metadatas', 'distances' e 'ids'
        """
        query_embedding = self.embedder.encode([query_text]).tolist()

        return self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )

    def delete(self, ids: List[str]) -> None:
        """Remove documentos do banco vetorial pelos seus IDs."""
        self.collection.delete(ids=ids)

    def count(self) -> int:
        """Retorna a quantidade de documentos indexados."""
        return self.collection.count()
