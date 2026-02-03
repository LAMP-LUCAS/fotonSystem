import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from pathlib import Path
from typing import List, Dict, Any
from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService
import logging

class VectorStore:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStore, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        try:
            # 1. Determine safe storage path (Local AppData)
            config_dir = BootstrapService.get_user_config_dir()
            self.db_path = config_dir / "memory_db"
            self.db_path.mkdir(parents=True, exist_ok=True)
            
            # 2. Add chroma logging suppression
            logging.getLogger("chromadb").setLevel(logging.ERROR)
            
            # 3. Initialize Client
            # Using PersistentClient for local storage
            self.client = chromadb.PersistentClient(path=str(self.db_path))
            
            # 4. Initialize Embedding Model (Lazy load could be better but we need it ready)
            # all-MiniLM-L6-v2 is fast and effective for semantic search
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            
            # 5. Get/Create Collection
            self.collection = self.client.get_or_create_collection(
                name="foton_knowledge_base",
                metadata={"hnsw:space": "cosine"} # Cosine similarity
            )
            
            logging.info(f"VectorStore initialized at {self.db_path}")
            
        except Exception as e:
            logging.error(f"Failed to initialize VectorStore: {e}")
            raise e

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """
        Generates embeddings and adds documents to the store.
        """
        if not documents:
            return
            
        # Generate Embeddings manually for control (and because we might swap models)
        embeddings = self.embedder.encode(documents).tolist()
        
        self.collection.upsert(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Semantically searches the knowledge base.
        """
        query_embedding = self.embedder.encode([query_text]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        return results

    def delete(self, ids: List[str]):
        self.collection.delete(ids=ids)
