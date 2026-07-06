"""
Migration Script — STORY-035

Converte coleção legada 'foton_knowledge_base' (v1.0, sem metadata de modelo)
para o novo padrão 'foton_minilm_384d' com metadata completa.

@story: STORY-035
@rule: RULE-RAG-10.7
"""

import logging
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class MigrationChecker:
    """Detecta e executa migração da coleção ChromaDB legada para o novo formato.

    A coleção v1.0 'foton_knowledge_base' não possui metadata de modelo.
    A v2.0 exige coleções nomeadas como 'foton_{model_tag}_{dimensions}d'
    com metadata contendo model_name, model_tag, dimensions, created_at.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self._client = None
        if db_path:
            self.db_path = db_path
        else:
            from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import (
                BootstrapService,
            )
            config_dir = BootstrapService.get_user_config_dir()
            self.db_path = config_dir / "memory_db"

    def _get_client(self):
        """Retorna cliente ChromaDB reutilizável (cache interno)."""
        if self._client is None:
            import chromadb
            self.db_path.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=str(self.db_path))
        return self._client

    def detect_legacy(self, client=None) -> bool:
        """Verifica se a coleção legada 'foton_knowledge_base' existe.

        Returns:
            True se a coleção legada existir, False caso contrário.
        """
        c = client or self._get_client()
        try:
            c.get_collection("foton_knowledge_base")
            return True
        except Exception:
            return False

    def run_migration(self, client=None) -> None:
        """Executa a migração completa:

        1. Lê todos os dados + embeddings da coleção legada
        2. Cria 'foton_minilm_384d' com metadata do modelo
        3. Copia dados para a nova coleção
        4. Cria backup 'foton_knowledge_base_legada'
        5. Remove a coleção original
        """
        c = client or self._get_client()

        logger.info("Migrando coleção 'foton_knowledge_base'...")

        legacy = c.get_collection("foton_knowledge_base")
        data = legacy.get(include=["embeddings", "documents", "metadatas"])

        count = len(data.get("ids", []))
        logger.info("Copiando %d chunks para nova coleção...", count)

        new_collection = c.get_or_create_collection(
            name="foton_minilm_384d",
            metadata={
                "hnsw:space": "cosine",
                "model_name": "paraphrase-multilingual-MiniLM-L12-v2",
                "model_tag": "minilm",
                "dimensions": "384",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
        )
        new_collection.add(
            embeddings=data["embeddings"],
            documents=data["documents"],
            metadatas=data["metadatas"],
            ids=data["ids"],
        )
        logger.info("Nova coleção 'foton_minilm_384d' criada com %d chunks.", count)

        backup = c.get_or_create_collection(
            name="foton_knowledge_base_legada",
            metadata={
                "hnsw:space": "cosine",
                "note": "Backup automático da coleção original — migração STORY-035",
            },
        )
        backup.add(
            embeddings=data["embeddings"],
            documents=data["documents"],
            metadatas=data["metadatas"],
            ids=data["ids"],
        )
        logger.info("Backup 'foton_knowledge_base_legada' criado.")

        c.delete_collection("foton_knowledge_base")
        logger.info("Coleção original 'foton_knowledge_base' removida.")
        logger.info("Migração concluída com sucesso!")

    def status_message(self) -> str:
        """Retorna mensagem legível sobre o estado da migração."""
        client = self._get_client()
        if self.detect_legacy(client):
            return (
                "Coleção legada 'foton_knowledge_base' detectada. "
                "Execute ensure_migrated() para migrar para 'foton_minilm_384d'. "
                "A coleção original será preservada como 'foton_knowledge_base_legada'."
            )
        return "Base de conhecimento já está no formato atualizado."

    def ensure_migrated(self) -> bool:
        """Entrypoint: detecta legado e executa migração se necessário.

        Returns:
            True se migração foi executada, False se já estava atualizado.
        """
        client = self._get_client()
        if self.detect_legacy(client):
            logger.warning(
                "Coleção legada 'foton_knowledge_base' detectada. "
                "Iniciando migração automática..."
            )
            self.run_migration(client)
            return True
        logger.info("Nenhuma migração necessária — base já atualizada.")
        return False
