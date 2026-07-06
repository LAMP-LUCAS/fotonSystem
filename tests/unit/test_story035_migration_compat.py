"""
Tests for STORY-035: Migration + Backward Compatibility

Covers:
- AC#1: migration.py detects foton_knowledge_base collection
- AC#2: Migration creates foton_minilm_384d copying data + metadata
- AC#3: Metadata contains {model_name, model_tag, dimensions, created_at}
- AC#4: Legacy collection renamed to _legada (backup)
- AC#5: No config 'rag' -> VectorStoreManager operates as MiniLM pure
- AC#6: No config + no migrated collection -> creates foton_minilm_384d from scratch
- AC#7: Clear message if migration needed

Rules:
- RULE-RAG-10.7: Backward compatibility
"""

import unittest
from unittest.mock import MagicMock, patch, call


class TestMigrationCheckerDetection(unittest.TestCase):
    """AC#1: Detect legacy collection"""

    @patch("chromadb.PersistentClient")
    def test_detect_legacy_returns_true_when_exists(self, MockChroma):
        from foton_system.core.rag.migration import MigrationChecker

        mock_client = MagicMock()
        mock_client.get_collection.return_value = MagicMock()
        MockChroma.return_value = mock_client

        checker = MigrationChecker.__new__(MigrationChecker)
        checker.db_path = MagicMock()

        result = checker.detect_legacy(mock_client)

        self.assertTrue(result)
        mock_client.get_collection.assert_called_once_with("foton_knowledge_base")

    @patch("chromadb.PersistentClient")
    def test_detect_legacy_returns_false_when_missing(self, MockChroma):
        from foton_system.core.rag.migration import MigrationChecker

        mock_client = MagicMock()
        mock_client.get_collection.side_effect = Exception("Not found")
        MockChroma.return_value = mock_client

        checker = MigrationChecker.__new__(MigrationChecker)
        checker.db_path = MagicMock()

        result = checker.detect_legacy(mock_client)

        self.assertFalse(result)

    @patch("chromadb.PersistentClient")
    def test_get_or_create_client_reuses(self, MockChroma):
        from foton_system.core.rag.migration import MigrationChecker
        from pathlib import Path

        mock_client = MagicMock()
        MockChroma.return_value = mock_client

        checker = MigrationChecker.__new__(MigrationChecker)
        checker._client = None
        checker.db_path = Path("/fake/path/memory_db")

        client1 = checker._get_client()
        client2 = checker._get_client()

        self.assertIs(client1, client2)
        MockChroma.assert_called_once()


class TestMigrationRunner(unittest.TestCase):
    """AC#2, AC#3, AC#4: Migration execution"""

    def setUp(self):
        from foton_system.core.rag.migration import MigrationChecker

        self.legacy_data = {
            "ids": ["id1", "id2"],
            "embeddings": [[0.1] * 384, [0.2] * 384],
            "documents": ["Documento A", "Documento B"],
            "metadatas": [{"source": "cliente1"}, {"source": "cliente2"}],
        }

        self.mock_legacy_collection = MagicMock()
        self.mock_legacy_collection.get.return_value = self.legacy_data

        self.mock_new_collection = MagicMock()
        self.mock_backup_collection = MagicMock()

        self.mock_client = MagicMock()
        def get_or_create_side_effect(name, **kwargs):
            if "legada" in name:
                return self.mock_backup_collection
            return self.mock_new_collection

        self.mock_client.get_or_create_collection.side_effect = get_or_create_side_effect
        self.mock_client.get_collection.return_value = self.mock_legacy_collection

        self.checker = MigrationChecker.__new__(MigrationChecker)
        self.checker.db_path = MagicMock()
        self.checker._client = self.mock_client

    def test_run_migration_copies_data_to_new_collection(self):
        """AC#2: Nova coleção recebe dados + embeddings"""
        self.checker.run_migration(self.mock_client)

        self.mock_client.get_or_create_collection.assert_any_call(
            name="foton_minilm_384d",
            metadata={
                "hnsw:space": "cosine",
                "model_name": "paraphrase-multilingual-MiniLM-L12-v2",
                "model_tag": "minilm",
                "dimensions": "384",
                "created_at": unittest.mock.ANY,
            },
        )

        self.mock_new_collection.add.assert_called_once_with(
            embeddings=self.legacy_data["embeddings"],
            documents=self.legacy_data["documents"],
            metadatas=self.legacy_data["metadatas"],
            ids=self.legacy_data["ids"],
        )

    def test_metadata_contains_required_fields(self):
        """AC#3: Metadata cont�m model_name, model_tag, dimensions, created_at"""
        self.checker.run_migration(self.mock_client)

        call_kwargs = None
        for call_args in self.mock_client.get_or_create_collection.call_args_list:
            if call_args.kwargs.get("name") == "foton_minilm_384d":
                call_kwargs = call_args.kwargs
                break

        self.assertIsNotNone(call_kwargs)
        meta = call_kwargs["metadata"]
        self.assertIn("model_name", meta)
        self.assertIn("model_tag", meta)
        self.assertIn("dimensions", meta)
        self.assertIn("created_at", meta)
        self.assertEqual(meta["model_tag"], "minilm")
        self.assertEqual(meta["dimensions"], "384")

    def test_run_migration_creates_backup_collection(self):
        """AC#4: Coleção legada vira _legada (backup)"""
        self.checker.run_migration(self.mock_client)

        self.mock_client.get_or_create_collection.assert_any_call(
            name="foton_knowledge_base_legada",
            metadata=unittest.mock.ANY,
        )

        self.mock_backup_collection.add.assert_called_once_with(
            embeddings=self.legacy_data["embeddings"],
            documents=self.legacy_data["documents"],
            metadatas=self.legacy_data["metadatas"],
            ids=self.legacy_data["ids"],
        )

    def test_run_migration_deletes_original_collection(self):
        """AC#4: Coleção original é deletada após migração"""
        self.checker.run_migration(self.mock_client)

        self.mock_client.delete_collection.assert_called_once_with("foton_knowledge_base")

    def test_run_migration_logs_progress(self):
        """Migração gera logs informativos"""
        with patch("logging.Logger.info") as mock_log:
            self.checker.run_migration(self.mock_client)

            self.assertGreater(len(mock_log.call_args_list), 0)
            log_messages = [args[0][0] for args in mock_log.call_args_list]
            has_progress = any("Migrando" in msg or "criada" in msg or "concluída" in msg for msg in log_messages)
            self.assertTrue(has_progress)


class TestMigrationMessage(unittest.TestCase):
    """AC#7: Mensagem clara ao usuário"""

    @patch("chromadb.PersistentClient")
    def test_status_message_when_migration_needed(self, MockChroma):
        from foton_system.core.rag.migration import MigrationChecker

        mock_client = MagicMock()
        mock_client.get_collection.return_value = MagicMock()
        MockChroma.return_value = mock_client

        checker = MigrationChecker.__new__(MigrationChecker)
        checker.db_path = MagicMock()
        checker._client = mock_client

        msg = checker.status_message()
        self.assertIn("foton_knowledge_base", msg)
        self.assertIn("migra", msg.lower())

    @patch("chromadb.PersistentClient")
    def test_status_message_when_no_migration_needed(self, MockChroma):
        from foton_system.core.rag.migration import MigrationChecker

        mock_client = MagicMock()
        mock_client.get_collection.side_effect = Exception("Not found")
        MockChroma.return_value = mock_client

        checker = MigrationChecker.__new__(MigrationChecker)
        checker.db_path = MagicMock()
        checker._client = mock_client

        msg = checker.status_message()
        self.assertTrue("atualizado" in msg.lower() or "ok" in msg.lower())


class TestMigrationHookInVectorStoreManager(unittest.TestCase):
    """AC#5, AC#6: Integração com VectorStoreManager"""

    @patch("chromadb.PersistentClient")
    @patch("sentence_transformers.SentenceTransformer")
    @patch("foton_system.core.rag.migration.MigrationChecker.detect_legacy")
    @patch("foton_system.core.rag.migration.MigrationChecker.run_migration")
    def test_lazy_init_triggers_migration_when_legacy_found(
        self, mock_run, mock_detect, MockST, MockChroma
    ):
        """Hook chama migration quando coleção legada existe"""
        mock_detect.return_value = True

        from foton_system.core.memory.vector_store import VectorStoreManager
        VectorStoreManager._instance = None

        mock_collection = MagicMock()
        MockChroma.return_value.get_or_create_collection.return_value = mock_collection

        manager = VectorStoreManager()
        manager._ensure_config_dir()
        manager._lazy_init()

        mock_run.assert_called_once()

    @patch("foton_system.core.rag.migration.MigrationChecker.run_migration")
    @patch("foton_system.core.rag.migration.MigrationChecker.detect_legacy")
    def test_no_migration_when_no_legacy(self, mock_detect, mock_run):
        """Sem coleção legada, run_migration não é chamada"""
        mock_detect.return_value = False

        from foton_system.core.memory.vector_store import VectorStoreManager
        VectorStoreManager._instance = None
        VectorStoreManager._instance = None

        manager = VectorStoreManager.__new__(VectorStoreManager)
        manager._initialized = True
        manager._lazy_init_done = False
        manager._instances = {}
        manager._active_tags = []
        manager._config_dir = MagicMock()

        with patch.object(manager, "_ensure_config_dir", return_value=MagicMock()):
            with patch("foton_system.core.memory.vector_store.VectorStoreInstance") as MockInstance:
                with patch("foton_system.modules.shared.infrastructure.config.config.Config") as MockConfig:
                    mock_config_instance = MagicMock()
                    mock_config_instance.rag_config = {"mode": "minilm"}
                    MockConfig.return_value = mock_config_instance

                    with patch("foton_system.core.rag.model_registry.ModelRegistry") as MockReg:
                        with patch("foton_system.core.rag.hardware_profiler.HardwareProfiler") as MockHW:
                            with patch("foton_system.core.rag.model_router.ModelRouter") as MockRouter:
                                MockRouter.resolve.return_value = ["minilm"]
                                MockRouter.validate_pipeline_feasibility.return_value = []
                                MockRouter.runtime_fallback.return_value = None

                                manager._lazy_init()

        mock_detect.assert_called_once()
        mock_run.assert_not_called()
        self.assertTrue(manager._lazy_init_done)


if __name__ == "__main__":
    unittest.main()
