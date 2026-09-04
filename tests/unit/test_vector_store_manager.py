"""
Tests for STORY-031: VectorStoreInstance + VectorStoreManager

Covers:
- RULE-RAG-10.1: VectorStoreManager is singleton
- RULE-RAG-10.2: VectorStoreInstance = embedder + collection + breaker
- RULE-RAG-10.3: Collection named foton_{tag}_{dims}d with metadata
- RULE-RAG-10.4: query dual mode merge by score without duplicates
- RULE-RAG-10.5: add_documents indexes in all active instances
- RULE-RAG-10.6: diagnostic aggregates multi-instance
- RULE-RAG-10.7: Backward compat: no config -> minilm legacy
"""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock


class TestVectorStoreManagerSingleton(unittest.TestCase):
    """RULE-RAG-10.1"""

    def test_singleton_pattern(self):
        from foton_system.core.memory.vector_store import VectorStoreManager

        VectorStoreManager._instance = None
        v1 = VectorStoreManager.__new__(VectorStoreManager)
        v2 = VectorStoreManager.__new__(VectorStoreManager)
        self.assertIs(v1, v2)

    def test_singleton_reset(self):
        from foton_system.core.memory.vector_store import VectorStoreManager

        VectorStoreManager._instance = None
        v1 = VectorStoreManager()
        VectorStoreManager._instance = None
        v2 = VectorStoreManager()
        self.assertIsNot(v1, v2)


class TestVectorStoreInstance(unittest.TestCase):
    """RULE-RAG-10.2, 10.3"""

    @patch("chromadb.PersistentClient")
    @patch("sentence_transformers.SentenceTransformer")
    def test_instance_creation_minilm(
        self, MockST, MockChromaClient
    ):
        from foton_system.core.memory.vector_store import VectorStoreInstance
        from foton_system.core.rag.model_registry import ModelEntry

        entry = ModelEntry(
            id="minilm",
            name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            type="embedding",
            dimensions=384,
            ram_required_gb=1.0,
            disk_required_gb=0.5,
        )

        mock_collection = MagicMock()
        MockChromaClient.return_value.get_or_create_collection.return_value = mock_collection

        config_dir = MagicMock()
        config_dir.__truediv__.return_value = config_dir

        instance = VectorStoreInstance.__new__(VectorStoreInstance)
        instance.model_tag = "minilm"
        instance.model_entry = entry
        instance.config_dir = config_dir
        instance.db_path = config_dir / "memory_db"
        instance._initialized = False
        instance._initialize()

        self.assertEqual(instance.model_tag, "minilm")
        self.assertEqual(instance.collection_name, "foton_minilm_384d")

        MockChromaClient.return_value.get_or_create_collection.assert_called_once()
        call_kwargs = MockChromaClient.return_value.get_or_create_collection.call_args[1]
        self.assertEqual(call_kwargs["name"], "foton_minilm_384d")
        self.assertIn("metadata", call_kwargs)
        self.assertEqual(call_kwargs["metadata"]["model_tag"], "minilm")
        self.assertEqual(call_kwargs["metadata"]["dimensions"], "384")

    @patch("chromadb.PersistentClient")
    @patch("sentence_transformers.SentenceTransformer")
    def test_instance_creation_bgem3(
        self, MockST, MockChromaClient
    ):
        from foton_system.core.memory.vector_store import VectorStoreInstance
        from foton_system.core.rag.model_registry import ModelEntry

        entry = ModelEntry(
            id="bgem3",
            name="BAAI/bge-m3",
            type="embedding",
            dimensions=1024,
            ram_required_gb=4.5,
            disk_required_gb=2.5,
        )

        config_dir = MagicMock()
        config_dir.__truediv__.return_value = config_dir

        instance = VectorStoreInstance.__new__(VectorStoreInstance)
        instance.model_tag = "bgem3"
        instance.model_entry = entry
        instance.config_dir = config_dir
        instance.db_path = config_dir / "memory_db"
        instance._initialized = False
        with patch("chromadb.PersistentClient") as MockChroma:
            with patch("sentence_transformers.SentenceTransformer"):
                mock_collection = MagicMock()
                MockChroma.return_value.get_or_create_collection.return_value = mock_collection
                instance._initialize()

        self.assertEqual(instance.collection_name, "foton_bgem3_1024d")

    def test_breaker_protected_operations(self):
        from foton_system.core.memory.vector_store import VectorStoreInstance
        from foton_system.core.memory.vector_store import CircuitBreakerOpenError
        from foton_system.core.rag.model_registry import ModelEntry

        entry = ModelEntry(
            id="minilm",
            name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            type="embedding",
            dimensions=384,
            ram_required_gb=1.0,
            disk_required_gb=0.5,
        )

        instance = VectorStoreInstance.__new__(VectorStoreInstance)
        instance.model_tag = "minilm"
        instance.model_entry = entry
        instance._initialized = True
        instance._breaker = MagicMock()
        instance._breaker.call = MagicMock(side_effect=CircuitBreakerOpenError("OPEN"))
        instance._do_count = MagicMock(return_value=42)

        result = instance.count()
        self.assertEqual(result, 0)

        result = instance.query("test")
        self.assertEqual(result["documents"], [[]])

        result = instance.add_documents(["doc"], [{}], ["id"])
        self.assertIsNone(result)


class TestVectorStoreManagerDualQuery(unittest.TestCase):
    """RULE-RAG-10.4"""

    def test_dual_mode_merge_by_score(self):
        from foton_system.core.memory.vector_store import VectorStoreManager

        mock_minilm = MagicMock()
        mock_minilm.query.return_value = {
            "documents": [["doc_minilm_A", "doc_minilm_B"]],
            "metadatas": [[{"source": "a"}, {"source": "b"}]],
            "distances": [[0.1, 0.3]],
            "ids": [["id_a", "id_b"]],
        }

        mock_bgem3 = MagicMock()
        mock_bgem3.query.return_value = {
            "documents": [["doc_bgem3_C", "doc_bgem3_D"]],
            "metadatas": [[{"source": "c"}, {"source": "d"}]],
            "distances": [[0.05, 0.2]],
            "ids": [["id_c", "id_d"]],
        }

        manager = VectorStoreManager.__new__(VectorStoreManager)
        manager._initialized = True
        manager._lazy_init_done = True
        manager._mode = "dual"
        manager._active_tags = ["minilm", "bgem3"]
        manager._instances = {"minilm": mock_minilm, "bgem3": mock_bgem3}

        result = manager.query("test query", n_results=3)

        docs = result.get("documents", [[]])[0]
        ids = result.get("ids", [[]])[0]

        self.assertEqual(len(docs), 3)
        self.assertEqual(len(set(ids)), 3)

        self.assertEqual(ids[0], "id_c")
        self.assertEqual(ids[1], "id_a")
        self.assertEqual(ids[2], "id_d")

    def test_single_mode_passthrough(self):
        from foton_system.core.memory.vector_store import VectorStoreManager

        mock_instance = MagicMock()
        mock_instance.query.return_value = {
            "documents": [["doc1"]],
            "metadatas": [[{"source": "a"}]],
            "distances": [[0.1]],
            "ids": [["id1"]],
        }

        manager = VectorStoreManager.__new__(VectorStoreManager)
        manager._initialized = True
        manager._lazy_init_done = True
        manager._mode = "minilm"
        manager._active_tags = ["minilm"]
        manager._instances = {"minilm": mock_instance}

        result = manager.query("test")

        self.assertEqual(result["documents"][0], ["doc1"])
        mock_instance.query.assert_called_once()


class TestVectorStoreManagerAddDocuments(unittest.TestCase):
    """RULE-RAG-10.5"""

    def test_add_documents_all_active_instances(self):
        from foton_system.core.memory.vector_store import VectorStoreManager

        mock_minilm = MagicMock()
        mock_bgem3 = MagicMock()

        manager = VectorStoreManager.__new__(VectorStoreManager)
        manager._initialized = True
        manager._lazy_init_done = True
        manager._mode = "dual"
        manager._active_tags = ["minilm", "bgem3"]
        manager._instances = {"minilm": mock_minilm, "bgem3": mock_bgem3}

        manager.add_documents(["doc1"], [{"source": "test"}], ["id1"])

        mock_minilm.add_documents.assert_called_once_with(
            ["doc1"], [{"source": "test"}], ["id1"]
        )
        mock_bgem3.add_documents.assert_called_once_with(
            ["doc1"], [{"source": "test"}], ["id1"]
        )

    def test_add_documents_empty_skips(self):
        from foton_system.core.memory.vector_store import VectorStoreManager

        manager = VectorStoreManager.__new__(VectorStoreManager)
        manager._initialized = True
        manager._lazy_init_done = True
        manager._active_tags = ["minilm"]
        manager._instances = {"minilm": MagicMock()}

        manager.add_documents([], [], [])
        manager._instances["minilm"].add_documents.assert_not_called()


class TestVectorStoreManagerDiagnostic(unittest.TestCase):
    """RULE-RAG-10.6"""

    def test_diagnostic_aggregates_multi_instance(self):
        from foton_system.core.memory.vector_store import VectorStoreManager

        mock_minilm = MagicMock()
        mock_minilm.diagnostic.return_value = {
            "model_tag": "minilm",
            "model_name": "MiniLM",
            "collection_name": "foton_minilm_384d",
            "total_chunks": 42,
            "circuit_breaker_status": "CLOSED",
            "ultima_indexacao": "2026-07-03",
        }

        mock_bgem3 = MagicMock()
        mock_bgem3.diagnostic.return_value = {
            "model_tag": "bgem3",
            "model_name": "BGE-M3",
            "collection_name": "foton_bgem3_1024d",
            "total_chunks": 10,
            "circuit_breaker_status": "CLOSED",
            "ultima_indexacao": "2026-07-03",
        }

        manager = VectorStoreManager.__new__(VectorStoreManager)
        manager._initialized = True
        manager._lazy_init_done = True
        manager._mode = "dual"
        manager._active_tags = ["minilm", "bgem3"]
        manager._instances = {"minilm": mock_minilm, "bgem3": mock_bgem3}

        diag = manager.diagnostic()

        self.assertEqual(diag["mode"], "dual")
        self.assertIn("minilm", diag["stores"])
        self.assertIn("bgem3", diag["stores"])
        self.assertEqual(diag["stores"]["minilm"]["total_chunks"], 42)
        self.assertEqual(diag["stores"]["bgem3"]["total_chunks"], 10)


class TestVectorStoreManagerBackwardCompat(unittest.TestCase):
    """RULE-RAG-10.7"""

    @patch("foton_system.core.memory.vector_store.VectorStoreManager._lazy_init")
    def test_manager_has_same_public_api_as_vectorstore(self, mock_lazy):
        from foton_system.core.memory.vector_store import VectorStoreManager

        manager = VectorStoreManager.__new__(VectorStoreManager)
        manager._initialized = True
        manager._lazy_init_done = True
        manager._mode = "minilm"
        manager._active_tags = ["minilm"]
        manager._instances = {"minilm": MagicMock()}

        self.assertTrue(hasattr(manager, "query"))
        self.assertTrue(hasattr(manager, "add_documents"))
        self.assertTrue(hasattr(manager, "delete"))
        self.assertTrue(hasattr(manager, "count"))
        self.assertTrue(hasattr(manager, "diagnostic"))
        self.assertTrue(hasattr(manager, "mark_indexed"))


if __name__ == "__main__":
    unittest.main()
