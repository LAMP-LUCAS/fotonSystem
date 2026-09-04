"""Tests for RAG config schema validation — STORY-040 [RULE-RAG-9.1] [RULE-RAG-9.4] [RULE-RAG-10.7] [RULE-RAG-11.5]"""

import unittest
from foton_system.modules.shared.infrastructure.config.rag_schema import (
    validate_rag_config,
    DEFAULT_RAG_CONFIG,
)


class TestValidateRagConfig(unittest.TestCase):
    def test_valid_full_config(self):
        config = {
            "embedding_mode": "bgem3",
            "pipeline": {
                "type": "rerank",
                "nodes": ["embed", "search", "rerank", "format"],
            },
            "models": {"primary": "bgem3", "fallback": ["minilm"]},
        }
        result = validate_rag_config(config)
        self.assertEqual(result["embedding_mode"], "bgem3")
        self.assertEqual(result["pipeline"]["type"], "rerank")
        self.assertEqual(
            result["pipeline"]["nodes"],
            ["embed", "search", "rerank", "format"],
        )
        self.assertEqual(result["models"]["primary"], "bgem3")
        self.assertEqual(result["models"]["fallback"], ["minilm"])

    def test_none_config_returns_defaults(self):
        result = validate_rag_config(None)
        self.assertEqual(result, DEFAULT_RAG_CONFIG)

    def test_empty_config_returns_defaults(self):
        result = validate_rag_config({})
        self.assertEqual(result, DEFAULT_RAG_CONFIG)

    def test_invalid_embedding_mode_falls_back(self):
        result = validate_rag_config({"embedding_mode": "gpt"})
        self.assertEqual(result["embedding_mode"], "minilm")

    def test_invalid_pipeline_type_falls_back(self):
        result = validate_rag_config({"pipeline": {"type": "invalid"}})
        self.assertEqual(result["pipeline"]["type"], "simple")

    def test_wrong_type_falls_back(self):
        result = validate_rag_config({"embedding_mode": 123})
        self.assertEqual(result["embedding_mode"], "minilm")

    def test_invalid_nodes_type_falls_back(self):
        result = validate_rag_config({"pipeline": {"nodes": "not_a_list"}})
        self.assertEqual(result["pipeline"]["nodes"], ["embed", "search", "format"])

    def test_unknown_field_ignored(self):
        result = validate_rag_config({"unknown_key": "value", "embedding_mode": "dual"})
        self.assertEqual(result["embedding_mode"], "dual")
        self.assertNotIn("unknown_key", result)

    def test_invalid_models_primary_falls_back(self):
        result = validate_rag_config({"models": {"primary": 42}})
        self.assertEqual(result["models"]["primary"], "minilm")

    def test_invalid_models_fallback_falls_back(self):
        result = validate_rag_config({"models": {"fallback": "not_a_list"}})
        self.assertEqual(result["models"]["fallback"], ["minilm"])

    def test_dual_mode_valid(self):
        result = validate_rag_config({"embedding_mode": "dual"})
        self.assertEqual(result["embedding_mode"], "dual")

    def test_simple_pipeline_valid(self):
        result = validate_rag_config({"pipeline": {"type": "simple"}})
        self.assertEqual(result["pipeline"]["type"], "simple")

    def test_partial_config_merges_with_defaults(self):
        result = validate_rag_config({"embedding_mode": "bgem3"})
        self.assertEqual(result["embedding_mode"], "bgem3")
        self.assertEqual(result["pipeline"]["type"], "simple")
        self.assertEqual(result["models"]["primary"], "minilm")


class TestConfigRagProperties(unittest.TestCase):
    def setUp(self):
        from foton_system.modules.shared.infrastructure.config.config import Config

        Config._instance = None
        self.config = Config()
        self.config._rag_validated = {
            "embedding_mode": "bgem3",
            "pipeline": {
                "type": "rerank",
                "nodes": ["embed", "search", "rerank", "format"],
            },
            "models": {"primary": "bgem3", "fallback": ["minilm"]},
        }

    def tearDown(self):
        from foton_system.modules.shared.infrastructure.config.config import Config

        Config._instance = None

    def test_rag_embedding_mode_property(self):
        self.assertEqual(self.config.rag_embedding_mode, "bgem3")

    def test_rag_pipeline_type_property(self):
        self.assertEqual(self.config.rag_pipeline_type, "rerank")

    def test_rag_models_primary_property(self):
        self.assertEqual(self.config.rag_models_primary, "bgem3")

    def test_rag_models_fallback_property(self):
        self.assertEqual(self.config.rag_models_fallback, ["minilm"])


class TestConfigRagPropertiesDefaults(unittest.TestCase):
    def setUp(self):
        from foton_system.modules.shared.infrastructure.config.config import Config

        Config._instance = None
        self.config = Config()
        self.config._rag_validated = {
            "embedding_mode": "minilm",
            "pipeline": {"type": "simple", "nodes": ["embed", "search", "format"]},
            "models": {"primary": "minilm", "fallback": ["minilm"]},
        }

    def tearDown(self):
        from foton_system.modules.shared.infrastructure.config.config import Config

        Config._instance = None

    def test_rag_embedding_mode_default(self):
        self.assertEqual(self.config.rag_embedding_mode, "minilm")

    def test_rag_pipeline_type_default(self):
        self.assertEqual(self.config.rag_pipeline_type, "simple")

    def test_rag_models_primary_default(self):
        self.assertEqual(self.config.rag_models_primary, "minilm")

    def test_rag_models_fallback_default(self):
        self.assertEqual(self.config.rag_models_fallback, ["minilm"])


if __name__ == "__main__":
    unittest.main()
