"""
Tests for OpQueryKnowledge

Covers:
- Input validation (empty query, invalid n_results)
- Successful query with mocked VectorStore
- Empty results handling
- Similarity score calculation from cosine distance
"""

import unittest
from unittest.mock import patch, MagicMock


class TestOpQueryKnowledgeValidation(unittest.TestCase):
    """Tests for validate() method."""

    def test_rejects_empty_query(self):
        """Should raise ValueError for empty query."""
        from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
        op = OpQueryKnowledge(actor="Test")

        with self.assertRaises(ValueError):
            op.validate(query="")

    def test_rejects_whitespace_only_query(self):
        """Should raise ValueError for whitespace-only query."""
        from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
        op = OpQueryKnowledge(actor="Test")

        with self.assertRaises(ValueError):
            op.validate(query="   ")

    def test_accepts_valid_query(self):
        """Should return validated dict for valid query."""
        from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
        op = OpQueryKnowledge(actor="Test")

        result = op.validate(query="projetos residenciais")

        self.assertEqual(result["query"], "projetos residenciais")
        self.assertEqual(result["n_results"], 5)

    def test_default_n_results(self):
        """Default n_results should be 5."""
        from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
        op = OpQueryKnowledge(actor="Test")

        result = op.validate(query="teste")

        self.assertEqual(result["n_results"], 5)

    def test_custom_n_results(self):
        """Custom n_results should be respected."""
        from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
        op = OpQueryKnowledge(actor="Test")

        result = op.validate(query="teste", n_results=10)

        self.assertEqual(result["n_results"], 10)

    def test_invalid_n_results_defaults_to_5(self):
        """Invalid n_results should default to 5."""
        from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
        op = OpQueryKnowledge(actor="Test")

        result = op.validate(query="teste", n_results=-1)

        self.assertEqual(result["n_results"], 5)


class TestOpQueryKnowledgeExecution(unittest.TestCase):
    """Tests for execute_logic() method."""

    @patch('foton_system.core.memory.vector_store.VectorStore')
    def test_returns_found_status_with_results(self, MockVectorStore):
        """Should return FOUND status when documents match."""
        mock_store = MagicMock()
        mock_store.query.return_value = {
            "documents": [["Documento sobre projeto residencial"]],
            "metadatas": [[{"filename": "INFO-SERVICO.md", "source": "/path/to/file"}]],
            "distances": [[0.2]]  # Low distance = high similarity
        }
        MockVectorStore.return_value = mock_store

        from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
        op = OpQueryKnowledge(actor="Test")

        result = op.execute_logic({"query": "projetos", "n_results": 5})

        self.assertEqual(result["status"], "FOUND")
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["results"][0]["source"], "INFO-SERVICO.md")
        self.assertAlmostEqual(result["results"][0]["score"], 0.8, places=3)

    @patch('foton_system.core.memory.vector_store.VectorStore')
    def test_returns_empty_status_when_no_documents(self, MockVectorStore):
        """Should return EMPTY status when no documents match."""
        mock_store = MagicMock()
        mock_store.query.return_value = {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }
        MockVectorStore.return_value = mock_store

        from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
        op = OpQueryKnowledge(actor="Test")

        result = op.execute_logic({"query": "não existe", "n_results": 5})

        self.assertEqual(result["status"], "EMPTY")
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["results"], [])


if __name__ == '__main__':
    unittest.main()
