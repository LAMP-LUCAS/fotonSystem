"""
VectorStore - Memória Semântica do FOTON System

Armazena e consulta documentos usando embeddings vetoriais (ChromaDB).
Modelo: paraphrase-multilingual-MiniLM-L12-v2 (otimizado para PT-BR).

DESIGN NOTES:
- Singleton para evitar múltiplas instâncias do modelo em memória
- Graceful degradation: falha na inicialização é logada mas não impede o sistema
- Persistência local em %LOCALAPPDATA%/FotonSystem/memory_db
"""

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
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
            from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService

            # 1. Caminho seguro de persistência (Local AppData)
            config_dir = BootstrapService.get_user_config_dir()
            self.db_path: Path = config_dir / "memory_db"
            self.db_path.mkdir(parents=True, exist_ok=True)

            # 2. Reduzir logs verbosos do ChromaDB
            logging.getLogger("chromadb").setLevel(logging.ERROR)

            # 3. Cliente persistente local
            self.client = chromadb.PersistentClient(path=str(self.db_path))

            # 4. Modelo de embeddings multilíngue (PT-BR otimizado)
            logger.info(f"Carregando modelo de embeddings: {EMBEDDING_MODEL}")
            self.embedder = SentenceTransformer(EMBEDDING_MODEL)

            # 5. Coleção com similaridade cosseno
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
