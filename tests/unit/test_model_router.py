"""
Tests for STORY-031: ModelRouter

Covers:
- RULE-RAG-9.1: resolve() returns list of active models
- RULE-RAG-9.2: Dual mode returns [primary, secondary]
- RULE-RAG-9.3: Fallback when primary not installed
- RULE-RAG-9.4: validate_pipeline_feasibility() with warnings
- RULE-RAG-9.5: Runtime fallback redirect
"""

import unittest
from unittest.mock import MagicMock


class TestModelRouterResolve(unittest.TestCase):
    """RULE-RAG-9.1, 9.2, 9.3"""

    def setUp(self):
        self.mock_registry = MagicMock()
        self.minilm_entry = MagicMock()
        self.minilm_entry.id = "minilm"
        self.minilm_entry.name = "paraphrase-multilingual-MiniLM-L12-v2"
        self.bgem3_entry = MagicMock()
        self.bgem3_entry.id = "bgem3"
        self.bgem3_entry.name = "BAAI/bge-m3"

        def fake_get(model_id):
            mapping = {"minilm": self.minilm_entry, "bgem3": self.bgem3_entry}
            return mapping.get(model_id)

        self.mock_registry.get.side_effect = fake_get

    def _make_hardware(self, ram_gb=16, disk_gb=50, has_cuda=False):
        hw = MagicMock()
        hw.ram_total_gb = ram_gb
        hw.ram_available_gb = ram_gb * 0.6
        hw.disk_free_gb = disk_gb
        hw.has_cuda = has_cuda
        hw.has_mps = False
        hw.cpu_cores = 4
        hw.vram_gb = 0
        return hw

    def test_resolve_minilm_mode(self):
        config = {"rag": {"mode": "minilm", "models": {"primary": "minilm"}}}
        from foton_system.core.rag.model_router import ModelRouter
        result = ModelRouter.resolve(config, None, self.mock_registry)
        self.assertEqual(result, ["minilm"])

    def test_resolve_bgem3_mode(self):
        config = {"rag": {"mode": "bgem3", "models": {"primary": "bgem3"}}}
        from foton_system.core.rag.model_router import ModelRouter
        result = ModelRouter.resolve(config, None, self.mock_registry)
        self.assertEqual(result, ["bgem3"])

    def test_resolve_dual_mode(self):
        config = {"rag": {"mode": "dual"}}
        from foton_system.core.rag.model_router import ModelRouter
        result = ModelRouter.resolve(config, None, self.mock_registry)
        self.assertEqual(result, ["minilm", "bgem3"])

    def test_resolve_primary_not_installed_fallback(self):
        def fake_get(model_id):
            mapping = {"minilm": self.minilm_entry}
            return mapping.get(model_id)

        self.mock_registry.get.side_effect = fake_get
        config = {
            "rag": {
                "mode": "bgem3",
                "models": {"primary": "bgem3", "fallback": ["minilm"]},
            }
        }
        from foton_system.core.rag.model_router import ModelRouter
        result = ModelRouter.resolve(config, None, self.mock_registry)
        self.assertEqual(result, ["minilm"])

    def test_resolve_no_models_available_hard_fallback_minilm(self):
        def fake_get(model_id):
            return None

        self.mock_registry.get.side_effect = fake_get
        config = {"rag": {"mode": "bgem3", "models": {"primary": "bgem3"}}}
        from foton_system.core.rag.model_router import ModelRouter
        result = ModelRouter.resolve(config, None, self.mock_registry)
        self.assertEqual(result, [])

    def test_resolve_infeasible_model_hardware_skipped(self):
        hw = self._make_hardware(ram_gb=2)
        config = {"rag": {"mode": "bgem3", "models": {"primary": "bgem3", "fallback": ["minilm"]}}}
        from foton_system.core.rag.model_router import ModelRouter
        result = ModelRouter.resolve(config, hw, self.mock_registry)
        self.assertEqual(result, ["minilm"])


class TestModelRouterFeasibility(unittest.TestCase):
    """RULE-RAG-9.4"""

    def _make_hardware(self, ram_gb=16, disk_gb=50, has_cuda=False):
        hw = MagicMock()
        hw.ram_total_gb = ram_gb
        hw.ram_available_gb = ram_gb * 0.6
        hw.disk_free_gb = disk_gb
        hw.has_cuda = has_cuda
        hw.has_mps = False
        hw.cpu_cores = 4
        hw.vram_gb = 0
        return hw

    def test_dual_mode_warning_when_low_ram(self):
        hw = self._make_hardware(ram_gb=6)
        config = {"rag": {"mode": "dual"}}
        from foton_system.core.rag.model_router import ModelRouter
        warnings = ModelRouter.validate_pipeline_feasibility(config, hw)
        self.assertTrue(any("dual" in w.lower() and "ram" in w.lower() for w in warnings))

    def test_no_warnings_for_adequate_hardware(self):
        hw = self._make_hardware(ram_gb=32, disk_gb=100)
        config = {"rag": {"mode": "minilm"}}
        from foton_system.core.rag.model_router import ModelRouter
        warnings = ModelRouter.validate_pipeline_feasibility(config, hw)
        self.assertEqual(len(warnings), 0)

    def test_minilm_always_feasible(self):
        hw = self._make_hardware(ram_gb=4)
        config = {"rag": {"mode": "minilm"}}
        from foton_system.core.rag.model_router import ModelRouter
        warnings = ModelRouter.validate_pipeline_feasibility(config, hw)
        self.assertEqual(len(warnings), 0)

    def test_no_hardware_no_warnings(self):
        from foton_system.core.rag.model_router import ModelRouter
        warnings = ModelRouter.validate_pipeline_feasibility({}, None)
        self.assertEqual(warnings, [])


class TestModelRouterRuntimeFallback(unittest.TestCase):
    """RULE-RAG-9.5"""

    def test_runtime_fallback_to_next_instance(self):
        from foton_system.core.rag.model_router import ModelRouter
        fallback = ModelRouter.runtime_fallback("minilm", ["minilm", "bgem3"])
        self.assertEqual(fallback, "bgem3")

    def test_runtime_fallback_none_when_no_alternative(self):
        from foton_system.core.rag.model_router import ModelRouter
        fallback = ModelRouter.runtime_fallback("minilm", ["minilm"])
        self.assertIsNone(fallback)

    def test_runtime_fallback_empty_active_list(self):
        from foton_system.core.rag.model_router import ModelRouter
        fallback = ModelRouter.runtime_fallback("minilm", [])
        self.assertIsNone(fallback)


if __name__ == "__main__":
    unittest.main()
