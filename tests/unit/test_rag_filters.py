"""
Tests for STORY-029: Filtros + Contexto + Diagnostico RAG

Covers:
- RULE-RAG-4.1: Filter by client
- RULE-RAG-4.2: Filter by tipo_doc
- RULE-RAG-4.3: Context snippet in results
- RULE-RAG-6.1: diagnostico_conhecimento tool
- RULE-RAG-6.2: Selective indexing by client
"""

import unittest
from unittest.mock import patch, MagicMock, PropertyMock


class TestVectorStoreQueryFilter(unittest.TestCase):
    """Tests for VectorStore.query() with where filter (RULE-RAG-4.1, 4.2)."""

    def _make_store(self):
        from foton_system.core.memory.vector_store import VectorStore
        store = VectorStore.__new__(VectorStore)
        store._initialized = True
        store._breaker = MagicMock()
        store._breaker.call = MagicMock(side_effect=lambda func, *a, **kw: func(*a, **kw))
        store.collection = MagicMock()
        store.embedder = MagicMock()
        mock_encoding = MagicMock()
        mock_encoding.tolist.return_value = [[0.1, 0.2, 0.3]]
        store.embedder.encode.return_value = mock_encoding
        return store

    def test_query_accepts_where_parameter(self):
        """_do_query should pass 'where' to ChromaDB collection.query()."""
        store = self._make_store()

        store.query("teste", n_results=5, where={"source": {"$contains": "ClienteX"}})

        call_kwargs = store.collection.query.call_args[1]
        self.assertIn("where", call_kwargs)
        self.assertEqual(call_kwargs["where"], {"source": {"$contains": "ClienteX"}})

    def test_query_where_none_omits_filter(self):
        """_do_query should omit 'where' when not provided."""
        store = self._make_store()

        store.query("teste", n_results=5)

        call_kwargs = store.collection.query.call_args[1]
        self.assertNotIn("where", call_kwargs)


class TestVectorStoreDiagnostic(unittest.TestCase):
    """Tests for VectorStore.diagnostic() (RULE-RAG-6.1)."""

    def _make_store(self):
        from foton_system.core.memory.vector_store import VectorStore
        from foton_system.core.memory.vector_store import CircuitBreakerOpenError
        store = VectorStore.__new__(VectorStore)
        store._initialized = True
        store._breaker = MagicMock()
        store._breaker.state = "CLOSED"
        store._breaker.last_exception = None
        store._breaker.call = MagicMock(side_effect=lambda func, *a, **kw: func(*a, **kw))
        store._do_count = MagicMock(return_value=42)
        store.count = VectorStore.count.__get__(store, VectorStore)
        db_path = MagicMock()
        marker = MagicMock()
        marker.exists.return_value = False
        db_path.__truediv__.return_value = marker
        store.db_path = db_path
        return store

    def test_diagnostic_returns_expected_structure(self):
        """diagnostic() should return total_chunks, circuit_breaker_status, ultima_indexacao."""
        store = self._make_store()

        result = store.diagnostic()

        self.assertIn("total_chunks", result)
        self.assertIn("circuit_breaker_status", result)
        self.assertIn("ultima_indexacao", result)
        self.assertEqual(result["total_chunks"], 42)
        self.assertEqual(result["circuit_breaker_status"], "CLOSED")

    def test_diagnostic_returns_open_status_when_breached(self):
        """diagnostic() should reflect OPEN circuit breaker state."""
        store = self._make_store()
        store._breaker.state = "OPEN"

        result = store.diagnostic()

        self.assertEqual(result["circuit_breaker_status"], "OPEN")
        self.assertEqual(result["ultima_indexacao"], "N/A")

    def test_diagnostic_handles_count_failure(self):
        """diagnostic() should handle count returning 0 gracefully."""
        store = self._make_store()
        store.count = MagicMock(return_value=0)

        result = store.diagnostic()

        self.assertEqual(result["total_chunks"], 0)
        self.assertEqual(result["circuit_breaker_status"], "CLOSED")


class TestOpQueryKnowledgeFilters(unittest.TestCase):
    """Tests for OpQueryKnowledge with filters (RULE-RAG-4.1, 4.2)."""

    def test_validate_accepts_cliente_param(self):
        """validate() should accept optional 'cliente' parameter."""
        from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
        op = OpQueryKnowledge(actor="Test")
        result = op.validate(query="teste", cliente="ClienteX")
        self.assertEqual(result["cliente"], "ClienteX")

    def test_validate_accepts_tipo_doc_param(self):
        """validate() should accept optional 'tipo_doc' parameter."""
        from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
        op = OpQueryKnowledge(actor="Test")
        result = op.validate(query="teste", tipo_doc="INFO")
        self.assertEqual(result["tipo_doc"], "INFO")

    def test_validate_defaults_filters_when_omitted(self):
        """validate() should default cliente/tipo_doc to empty when omitted."""
        from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
        op = OpQueryKnowledge(actor="Test")
        result = op.validate(query="teste")
        self.assertEqual(result["cliente"], "")
        self.assertEqual(result["tipo_doc"], "")

    def test_validate_accepts_both_filters(self):
        """validate() should accept both cliente and tipo_doc simultaneously."""
        from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
        op = OpQueryKnowledge(actor="Test")
        result = op.validate(query="teste", cliente="ClienteX", tipo_doc="INFO")
        self.assertEqual(result["cliente"], "ClienteX")
        self.assertEqual(result["tipo_doc"], "INFO")

    @patch('foton_system.core.memory.vector_store.VectorStore')
    def test_execute_logic_passes_where_to_store(self, MockVectorStore):
        """execute_logic should build where filter from cliente/tipo_doc."""
        mock_store = MagicMock()
        mock_store.query.return_value = {
            "documents": [["doc1"]],
            "metadatas": [[{"filename": "INFO.md", "source": "/ClienteX/path"}]],
            "distances": [[0.1]]
        }
        MockVectorStore.return_value = mock_store

        from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
        op = OpQueryKnowledge(actor="Test")
        result = op.execute_logic({
            "query": "teste",
            "n_results": 5,
            "cliente": "ClienteX",
            "tipo_doc": "INFO"
        })

        call_kwargs = mock_store.query.call_args[1]
        self.assertEqual(result["status"], "FOUND")
        self.assertIn("where", call_kwargs)
        self.assertIn("source", call_kwargs["where"])
        self.assertIn("filename", call_kwargs["where"])

    @patch('foton_system.core.memory.vector_store.VectorStore')
    def test_execute_logic_no_filters_omits_where(self, MockVectorStore):
        """execute_logic should not pass where when no filters."""
        mock_store = MagicMock()
        mock_store.query.return_value = {
            "documents": [["doc1"]],
            "metadatas": [[{"filename": "INFO.md", "source": "/path"}]],
            "distances": [[0.1]]
        }
        MockVectorStore.return_value = mock_store

        from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
        op = OpQueryKnowledge(actor="Test")
        result = op.execute_logic({
            "query": "teste",
            "n_results": 5,
            "cliente": "",
            "tipo_doc": ""
        })

        call_kwargs = mock_store.query.call_args[1]
        self.assertNotIn("where", call_kwargs)


class TestOpQueryKnowledgeContexto(unittest.TestCase):
    """Tests for context snippet in results (RULE-RAG-4.3)."""

    @patch('foton_system.core.memory.vector_store.VectorStore')
    def test_results_include_contexto_field(self, MockVectorStore):
        """Results should include 'contexto' field."""
        mock_store = MagicMock()
        mock_store.query.return_value = {
            "documents": [["Documento sobre projeto residencial em Sao Paulo"]],
            "metadatas": [[{"filename": "INFO.md", "source": "/path"}]],
            "distances": [[0.2]]
        }
        MockVectorStore.return_value = mock_store

        from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
        op = OpQueryKnowledge(actor="Test")
        result = op.execute_logic({
            "query": "projeto residencial",
            "n_results": 5,
            "cliente": "",
            "tipo_doc": ""
        })

        self.assertIn("contexto", result["results"][0])
        self.assertIsInstance(result["results"][0]["contexto"], str)

    @patch('foton_system.core.memory.vector_store.VectorStore')
    def test_contexto_markers_present(self, MockVectorStore):
        """Contexto should contain visual markers around relevant portion."""
        mock_store = MagicMock()
        mock_store.query.return_value = {
            "documents": [["Documento sobre projeto residencial em Sao Paulo"]],
            "metadatas": [[{"filename": "INFO.md", "source": "/path"}]],
            "distances": [[0.2]]
        }
        MockVectorStore.return_value = mock_store

        from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
        op = OpQueryKnowledge(actor="Test")
        result = op.execute_logic({
            "query": "projeto residencial",
            "n_results": 5,
            "cliente": "",
            "tipo_doc": ""
        })

        ctx = result["results"][0]["contexto"]
        self.assertIn(">>>", ctx)
        self.assertIn("<<<", ctx)

    @patch('foton_system.core.memory.vector_store.VectorStore')
    def test_contexto_includes_original_document_fallback(self, MockVectorStore):
        """For short chunks, contexto should include the full document text."""
        mock_store = MagicMock()
        mock_store.query.return_value = {
            "documents": [["texto curto"]],
            "metadatas": [[{"filename": "INFO.md", "source": "/path"}]],
            "distances": [[0.2]]
        }
        MockVectorStore.return_value = mock_store

        from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
        op = OpQueryKnowledge(actor="Test")
        result = op.execute_logic({
            "query": "texto curto",
            "n_results": 5,
            "cliente": "",
            "tipo_doc": ""
        })

        self.assertIn("texto curto", result["results"][0]["contexto"])


class TestOpIndexKnowledgeSeletivo(unittest.TestCase):
    """Tests for selective indexing by client (RULE-RAG-6.2)."""

    @patch('foton_system.core.ops.op_index_knowledge.Config')
    def test_validate_accepts_cliente(self, MockConfig):
        """validate() should accept 'cliente' param and build target_path."""
        MockConfig_instance = MagicMock()
        MockConfig_instance.base_pasta_clientes = MagicMock()
        MockConfig_instance.base_pasta_clientes.__truediv__.return_value = MagicMock()
        MockConfig.return_value = MockConfig_instance

        from foton_system.core.ops.op_index_knowledge import OpIndexKnowledge
        op = OpIndexKnowledge(actor="Test")
        result = op.validate(cliente="ClienteX")

        self.assertIn("target_path_obj", result)
        self.assertIn("cliente", result)
        self.assertEqual(result["cliente"], "ClienteX")

    def test_validate_without_cliente_defaults_to_all(self):
        """validate() without cliente should fallback to default behavior."""
        from foton_system.core.ops.op_index_knowledge import OpIndexKnowledge
        op = OpIndexKnowledge(actor="Test")
        result = op.validate()

        self.assertNotIn("cliente", result)
        self.assertIn("target_path_obj", result)


class TestDiagnosticMCPTool(unittest.TestCase):
    """Tests for diagnostico_conhecimento MCP tool (RULE-RAG-6.1)."""

    @patch('foton_system.core.memory.vector_store.VectorStore')
    def test_diagnostico_returns_expected_format(self, MockVectorStore):
        """diagnostico_conhecimento should return formatted diagnostic string."""
        mock_store = MagicMock()
        mock_store.diagnostic.return_value = {
            "total_chunks": 42,
            "circuit_breaker_status": "CLOSED",
            "ultima_indexacao": "2026-07-02 10:00:00"
        }
        MockVectorStore.return_value = mock_store

        from foton_system.interfaces.mcp.foton_mcp import diagnostico_conhecimento
        result = diagnostico_conhecimento()

        self.assertIn("42", result)
        self.assertIn("CLOSED", result)
        self.assertIn("2026-07-02", result)


if __name__ == '__main__':
    unittest.main()
