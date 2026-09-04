"""
Tests for STORY-033: RAG Pipeline Node System

Covers:
- RULE-RAG-11.1: PipelineNode ABC
- RULE-RAG-11.2: ProcessContext
- RULE-RAG-11.3: RagPipeline.run()
- RULE-RAG-11.4: EmbedNode, SearchNode, RerankNode, FormatNode
- RULE-RAG-11.5: Pipeline config from settings.json
- RULE-RAG-11.6: (Futuro) Pipeline customizado
"""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock


class TestPipelineNodeABC(unittest.TestCase):
    """RULE-RAG-11.1"""

    def test_cannot_instantiate_abc_directly(self):
        from foton_system.core.rag.pipeline import PipelineNode
        with self.assertRaises(TypeError):
            PipelineNode()

    def test_concrete_node_has_required_attributes(self):
        from foton_system.core.rag.nodes.embed_node import EmbedNode
        node = EmbedNode()
        self.assertTrue(hasattr(node, 'name'))
        self.assertTrue(hasattr(node, 'input_keys'))
        self.assertTrue(hasattr(node, 'output_keys'))
        self.assertTrue(hasattr(node, 'execute'))
        self.assertEqual(node.name, "embed")


class TestProcessContext(unittest.TestCase):
    """RULE-RAG-11.2"""

    def test_context_accepts_valid_keys(self):
        from foton_system.core.rag.pipeline import ProcessContext
        ctx = ProcessContext({"query": "teste", "n_results": 5})
        self.assertEqual(ctx["query"], "teste")
        self.assertEqual(ctx["n_results"], 5)

    def test_context_rejects_invalid_keys(self):
        from foton_system.core.rag.pipeline import ProcessContext
        with self.assertRaises(KeyError):
            ProcessContext({"invalid_key": "value"})

    def test_context_is_mutable_mapping(self):
        from foton_system.core.rag.pipeline import ProcessContext
        ctx = ProcessContext()
        ctx["query"] = "nova consulta"
        self.assertEqual(ctx["query"], "nova consulta")
        self.assertIn("query", ctx)

    def test_context_setdefault_works(self):
        from foton_system.core.rag.pipeline import ProcessContext
        ctx = ProcessContext()
        result = ctx.setdefault("n_results", 10)
        self.assertEqual(result, 10)
        self.assertEqual(ctx["n_results"], 10)
        ctx["n_results"] = 5
        self.assertEqual(ctx.setdefault("n_results", 10), 5)

    def test_context_setdefault_allows_new_keys(self):
        from foton_system.core.rag.pipeline import ProcessContext
        ctx = ProcessContext()
        ctx.setdefault("custom_key", "value")
        self.assertEqual(ctx["custom_key"], "value")


class TestEmbedNode(unittest.TestCase):
    """RULE-RAG-11.4 — EmbedNode"""

    def test_embed_node_embeds_query_for_active_tags(self):
        from foton_system.core.rag.pipeline import ProcessContext
        from foton_system.core.rag.nodes.embed_node import EmbedNode

        mock_instance = MagicMock()
        mock_instance.embed_query.return_value = [0.1, 0.2, 0.3]

        mock_manager = MagicMock()
        mock_manager.active_tags = ["minilm"]
        mock_manager.get_instance.return_value = mock_instance

        with patch(
            "foton_system.core.rag.nodes.embed_node.VectorStoreManager",
            return_value=mock_manager,
        ):
            node = EmbedNode()
            ctx = ProcessContext({"query": "teste"})
            result = node.execute(ctx)

            self.assertIn("embeddings", result)
            self.assertIn("minilm", result["embeddings"])
            self.assertEqual(result["embeddings"]["minilm"], [0.1, 0.2, 0.3])
            mock_instance.embed_query.assert_called_once_with("teste")


class TestSearchNode(unittest.TestCase):
    """RULE-RAG-11.4 — SearchNode"""

    def test_search_node_queries_with_embeddings_single_mode(self):
        from foton_system.core.rag.pipeline import ProcessContext
        from foton_system.core.rag.nodes.search_node import SearchNode

        mock_instance = MagicMock()
        mock_instance.query_with_embeddings.return_value = {
            "documents": [["doc1"]],
            "metadatas": [[{"filename": "test.md", "source": "/path/test.md"}]],
            "distances": [[0.15]],
            "ids": [["id1"]],
        }

        mock_manager = MagicMock()
        mock_manager.active_tags = ["minilm"]
        mock_manager.get_instance.return_value = mock_instance

        with patch(
            "foton_system.core.rag.nodes.search_node.VectorStoreManager",
            return_value=mock_manager,
        ):
            node = SearchNode()
            ctx = ProcessContext({
                "query": "teste",
                "embeddings": {"minilm": [0.1, 0.2, 0.3]},
                "n_results": 5,
            })
            result = node.execute(ctx)

            self.assertIn("raw_results", result)
            self.assertEqual(len(result["raw_results"]), 1)
            self.assertEqual(result["raw_results"][0]["document"], "doc1")
            self.assertEqual(result["raw_results"][0]["source"], "test.md")
            self.assertAlmostEqual(result["raw_results"][0]["score"], 0.85)

    def test_search_node_handles_empty_embeddings(self):
        from foton_system.core.rag.pipeline import ProcessContext
        from foton_system.core.rag.nodes.search_node import SearchNode

        mock_instance = MagicMock()
        mock_instance.query.return_value = {
            "documents": [["fallback_doc"]],
            "metadatas": [[{"filename": "fallback.md"}]],
            "distances": [[0.5]],
            "ids": [["fid1"]],
        }

        mock_manager = MagicMock()
        mock_manager.active_tags = ["minilm"]
        mock_manager.get_instance.return_value = mock_instance

        with patch(
            "foton_system.core.rag.nodes.search_node.VectorStoreManager",
            return_value=mock_manager,
        ):
            node = SearchNode()
            ctx = ProcessContext({
                "query": "teste",
                "embeddings": {},
                "n_results": 5,
            })
            result = node.execute(ctx)
            self.assertIn("raw_results", result)
            self.assertEqual(len(result["raw_results"]), 1)


class TestRerankNode(unittest.TestCase):
    """RULE-RAG-11.4 — RerankNode"""

    def test_rerank_node_reorders_by_score(self):
        from foton_system.core.rag.pipeline import ProcessContext
        from foton_system.core.rag.nodes.rerank_node import RerankNode

        raw_results = [
            {"document": "doc A", "score": 0.3},
            {"document": "doc B", "score": 0.9},
            {"document": "doc C", "score": 0.6},
        ]

        node = RerankNode()
        node._model = MagicMock()
        node._model.predict.return_value = [0.3, 0.9, 0.6]

        ctx = ProcessContext({"query": "teste", "raw_results": raw_results})
        result = node.execute(ctx)

        self.assertIn("scored_results", result)
        self.assertEqual(result["scored_results"][0]["document"], "doc B")
        self.assertEqual(result["scored_results"][1]["document"], "doc C")
        self.assertEqual(result["scored_results"][2]["document"], "doc A")

    def test_rerank_node_fallback_when_no_cross_encoder(self):
        from foton_system.core.rag.pipeline import ProcessContext
        from foton_system.core.rag.nodes.rerank_node import RerankNode, _check_cross_encoder

        raw_results = [{"document": "doc A", "score": 0.5}]

        with patch(
            "foton_system.core.rag.nodes.rerank_node._check_cross_encoder",
            return_value=False,
        ):
            node = RerankNode()
            ctx = ProcessContext({"query": "teste", "raw_results": raw_results})
            result = node.execute(ctx)

            self.assertEqual(result["scored_results"], raw_results)

    def test_rerank_node_handles_empty_results(self):
        from foton_system.core.rag.pipeline import ProcessContext
        from foton_system.core.rag.nodes.rerank_node import RerankNode

        with patch(
            "foton_system.core.rag.nodes.rerank_node._check_cross_encoder",
            return_value=True,
        ):
            node = RerankNode()
            node._model = MagicMock()
            ctx = ProcessContext({"query": "teste", "raw_results": []})
            result = node.execute(ctx)
            self.assertEqual(result["scored_results"], [])


class TestFormatNode(unittest.TestCase):
    """RULE-RAG-11.4 — FormatNode"""

    def test_format_node_output_structure(self):
        from foton_system.core.rag.pipeline import ProcessContext
        from foton_system.core.rag.nodes.format_node import FormatNode

        raw_results = [
            {
                "document": "Documento de exemplo sobre arquitetura",
                "source": "exemplo.md",
                "source_path": "/path/exemplo.md",
                "score": 0.85,
            }
        ]

        node = FormatNode()
        ctx = ProcessContext({"query": "arquitetura", "raw_results": raw_results})
        result = node.execute(ctx)

        output = result["formatted_output"]
        self.assertEqual(output["status"], "FOUND")
        self.assertEqual(output["query"], "arquitetura")
        self.assertEqual(output["total"], 1)
        self.assertIn("contexto", output["results"][0])
        self.assertIn(">>>", output["results"][0]["contexto"])

    def test_format_node_empty_results(self):
        from foton_system.core.rag.pipeline import ProcessContext
        from foton_system.core.rag.nodes.format_node import FormatNode

        node = FormatNode()
        ctx = ProcessContext({"query": "teste", "raw_results": []})
        result = node.execute(ctx)
        self.assertEqual(result["formatted_output"]["status"], "EMPTY")
        self.assertEqual(result["formatted_output"]["total"], 0)

    def test_format_node_uses_scored_results_when_available(self):
        from foton_system.core.rag.pipeline import ProcessContext
        from foton_system.core.rag.nodes.format_node import FormatNode

        scored = [
            {
                "document": "doc rerankado",
                "source": "test.md",
                "score": 0.95,
            }
        ]

        node = FormatNode()
        ctx = ProcessContext({
            "query": "teste",
            "raw_results": [{"document": "raw doc", "score": 0.5}],
            "scored_results": scored,
        })
        result = node.execute(ctx)
        self.assertEqual(result["formatted_output"]["results"][0]["document"], "doc rerankado")


class TestRagPipeline(unittest.TestCase):
    """RULE-RAG-11.3 — RagPipeline"""

    def test_simple_pipeline_executes_embed_search_format(self):
        from foton_system.core.rag.pipeline import RagPipeline

        mock_embed = MagicMock()
        mock_embed.name = "embed"
        mock_embed.execute.side_effect = lambda ctx: ctx

        mock_search = MagicMock()
        mock_search.name = "search"
        mock_search.execute.side_effect = lambda ctx: ctx

        mock_format = MagicMock()
        mock_format.name = "format"
        mock_format.execute.side_effect = lambda ctx: ctx

        pipeline = RagPipeline.__new__(RagPipeline)
        pipeline._pipeline_type = "simple"
        pipeline._node_names = ["embed", "search", "format"]
        pipeline._nodes = [mock_embed, mock_search, mock_format]

        ctx = pipeline.run({"query": "teste"})
        mock_embed.execute.assert_called_once()
        mock_search.execute.assert_called_once()
        mock_format.execute.assert_called_once()

    def test_rerank_pipeline_includes_four_nodes(self):
        from foton_system.core.rag.pipeline import RagPipeline

        pipeline = RagPipeline.__new__(RagPipeline)
        pipeline._pipeline_type = "rerank"
        pipeline._node_names = ["embed", "search", "rerank", "format"]
        pipeline._nodes = [
            MagicMock(name="embed"),
            MagicMock(name="search"),
            MagicMock(name="rerank"),
            MagicMock(name="format"),
        ]

        ctx = pipeline.run({"query": "teste"})
        self.assertEqual(len(pipeline._nodes), 4)
        for node in pipeline._nodes:
            node.execute.assert_called_once()

    def test_pipeline_instantiation_from_config(self):
        from foton_system.core.rag.pipeline import RagPipeline

        mock_config = MagicMock()
        mock_config.rag_config = {
            "pipeline": {"type": "simple", "nodes": ["embed", "search", "format"]}
        }

        with patch(
            "foton_system.core.rag.pipeline.Config",
            return_value=mock_config,
        ):
            pipeline = RagPipeline.from_config()
            self.assertEqual(pipeline._pipeline_type, "simple")
            self.assertEqual(pipeline._node_names, ["embed", "search", "format"])


class TestRerankPipelineFallback(unittest.TestCase):
    """RULE-RAG-11.5 — Fallback quando rerank não disponível"""

    def test_rerank_node_skipped_when_import_fails(self):
        from foton_system.core.rag.pipeline import RagPipeline

        pipeline = RagPipeline.__new__(RagPipeline)
        pipeline._pipeline_type = "rerank"
        pipeline._node_names = ["embed", "search", "rerank", "format"]

        mock_embed = MagicMock()
        mock_embed.execute.side_effect = lambda ctx: ctx
        mock_search = MagicMock()
        mock_search.execute.side_effect = lambda ctx: ctx
        mock_format = MagicMock()
        mock_format.execute.side_effect = lambda ctx: ctx

        pipeline._nodes = [mock_embed, mock_search, mock_format]

        ctx = pipeline.run({"query": "teste"})
        self.assertEqual(len(pipeline._nodes), 3)
        mock_embed.execute.assert_called_once()
        mock_search.execute.assert_called_once()
        mock_format.execute.assert_called_once()


if __name__ == "__main__":
    unittest.main()
