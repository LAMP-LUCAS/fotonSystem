# @story: STORY-030
# @rule: RULE-RAG-8.1, RULE-RAG-8.2, RULE-RAG-8.3, RULE-RAG-8.4

import unittest
from unittest.mock import patch, MagicMock


class TestModelRegistrySingleton(unittest.TestCase):
    """Tests for ModelRegistry singleton behavior — RULE-RAG-8.1."""

    def tearDown(self):
        from foton_system.core.rag.model_registry import ModelRegistry
        ModelRegistry._instance = None

    def test_singleton_returns_same_instance(self):
        from foton_system.core.rag.model_registry import ModelRegistry
        r1 = ModelRegistry()
        r2 = ModelRegistry()
        self.assertIs(r1, r2)

    def test_registry_contains_minilm(self):
        from foton_system.core.rag.model_registry import ModelRegistry
        registry = ModelRegistry()
        models = registry.list_models()
        model_ids = [m.id for m in models]
        self.assertIn("minilm", model_ids)

    def test_registry_contains_bgem3(self):
        from foton_system.core.rag.model_registry import ModelRegistry
        registry = ModelRegistry()
        models = registry.list_models()
        model_ids = [m.id for m in models]
        self.assertIn("bgem3", model_ids)

    def test_minilm_has_384_dimensions(self):
        from foton_system.core.rag.model_registry import ModelRegistry
        registry = ModelRegistry()
        model = registry.get("minilm")
        self.assertEqual(model.dimensions, 384)

    def test_bgem3_has_1024_dimensions(self):
        from foton_system.core.rag.model_registry import ModelRegistry
        registry = ModelRegistry()
        model = registry.get("bgem3")
        self.assertEqual(model.dimensions, 1024)

    def test_minilm_is_embedding_type(self):
        from foton_system.core.rag.model_registry import ModelRegistry
        registry = ModelRegistry()
        model = registry.get("minilm")
        self.assertEqual(model.type, "embedding")

    def test_minilm_name_includes_org_prefix(self):
        from foton_system.core.rag.model_registry import ModelRegistry
        registry = ModelRegistry()
        model = registry.get("minilm")
        self.assertIn("sentence-transformers/", model.name,
                      "O nome do modelo deve conter o prefixo 'sentence-transformers/' "
                      "para que o is_installed() encontre o cache HF correto "
                      "(models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2)")

    def test_bgem3_requires_more_ram(self):
        from foton_system.core.rag.model_registry import ModelRegistry
        registry = ModelRegistry()
        minilm = registry.get("minilm")
        bgem3 = registry.get("bgem3")
        self.assertGreater(bgem3.ram_required_gb, minilm.ram_required_gb)

    def test_get_unknown_model_returns_none(self):
        from foton_system.core.rag.model_registry import ModelRegistry
        registry = ModelRegistry()
        self.assertIsNone(registry.get("modelo_inexistente"))


class TestModelRegistryIsInstalled(unittest.TestCase):
    """Tests for is_installed() — RULE-RAG-8.2."""

    def setUp(self):
        self._patcher_path = patch('foton_system.core.rag.model_registry.Path')
        self.mock_path = self._patcher_path.start()
        self.addCleanup(self._patcher_path.stop)

        mock_home = MagicMock()
        self.mock_path.return_value = mock_home
        mock_hub = MagicMock()
        mock_home.__truediv__.return_value = mock_hub
        self._mock_model_path = MagicMock()
        mock_hub.__truediv__.return_value = self._mock_model_path

    def tearDown(self):
        from foton_system.core.rag.model_registry import ModelRegistry
        ModelRegistry._instance = None

    def test_is_installed_returns_true_when_model_exists(self):
        self._mock_model_path.exists.return_value = True
        from foton_system.core.rag.model_registry import ModelRegistry
        registry = ModelRegistry()
        self.assertTrue(registry.is_installed("minilm"))

    def test_is_installed_returns_false_when_model_missing(self):
        self._mock_model_path.exists.return_value = False
        from foton_system.core.rag.model_registry import ModelRegistry
        registry = ModelRegistry()
        self.assertFalse(registry.is_installed("minilm"))

    def test_is_installed_unknown_model_returns_false(self):
        from foton_system.core.rag.model_registry import ModelRegistry
        registry = ModelRegistry()
        self.assertFalse(registry.is_installed("modelo_inexistente"))


class TestModelRegistryAvailableModels(unittest.TestCase):
    """Tests for available_models() — RULE-RAG-8.3."""

    def tearDown(self):
        from foton_system.core.rag.model_registry import ModelRegistry
        ModelRegistry._instance = None

    def _make_profile(self, ram_available_gb=8.0, has_cuda=False):
        from foton_system.core.rag.hardware_profiler import HardwareProfile
        return HardwareProfile(
            cpu_cores=4, ram_total_gb=ram_available_gb + 2,
            ram_available_gb=ram_available_gb, has_cuda=has_cuda,
            cuda_version="", has_mps=False, vram_gb=0, disk_free_gb=100
        )

    def test_available_excludes_bgem3_with_low_ram(self):
        from foton_system.core.rag.model_registry import ModelRegistry
        registry = ModelRegistry()
        profile = self._make_profile(ram_available_gb=4.0)
        available = registry.available_models(profile)
        ids = [m.id for m in available]
        self.assertIn("minilm", ids)
        self.assertNotIn("bgem3", ids)

    def test_available_includes_bgem3_with_high_ram(self):
        from foton_system.core.rag.model_registry import ModelRegistry
        registry = ModelRegistry()
        profile = self._make_profile(ram_available_gb=16.0)
        available = registry.available_models(profile)
        ids = [m.id for m in available]
        self.assertIn("minilm", ids)
        self.assertIn("bgem3", ids)

    def test_bgem3_requires_gpu_flag_when_no_cuda(self):
        from foton_system.core.rag.model_registry import ModelRegistry
        registry = ModelRegistry()
        bgem3 = registry.get("bgem3")
        self.assertFalse(bgem3.requires_gpu)


class TestModelRegistryExtensible(unittest.TestCase):
    """Tests for extensibility via register_model() — RULE-RAG-8.4."""

    def tearDown(self):
        from foton_system.core.rag.model_registry import ModelRegistry
        ModelRegistry._instance = None

    def test_register_new_model(self):
        from foton_system.core.rag.model_registry import ModelRegistry, ModelEntry
        registry = ModelRegistry()
        custom = ModelEntry(
            id="test-model", name="test/test-model", type="embedding",
            dimensions=128, ram_required_gb=1.0, disk_required_gb=0.5,
            requires_gpu=False, is_default=False
        )
        registry.register(custom)
        retrieved = registry.get("test-model")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, "test-model")

    def test_register_overwrites_existing(self):
        from foton_system.core.rag.model_registry import ModelRegistry, ModelEntry
        registry = ModelRegistry()
        override = ModelEntry(
            id="minilm", name="custom/minilm", type="embedding",
            dimensions=256, ram_required_gb=0.5, disk_required_gb=0.3,
            requires_gpu=False, is_default=False
        )
        registry.register(override)
        model = registry.get("minilm")
        self.assertEqual(model.dimensions, 256)
        self.assertEqual(model.name, "custom/minilm")


if __name__ == '__main__':
    unittest.main()
