"""
Tests for STORY-037: MCP diagnostico_conhecimento multi-modelo

Covers:
- RULE-RAG-10.6: VectorStoreManager.diagnostic() multi-instance
- RULE-RAG-10.7: Backward compat: no config -> minilm legacy
- RULE-RAG-6.2: total_chunks, cb_status, ultima_indexacao
"""

import unittest
from unittest.mock import patch, MagicMock


class TestDiagnosticoConhecimentoMultiColecao(unittest.TestCase):
    """STORY-037 AC1, AC2: Multi-colecao exibe mode + todos os campos."""

    @patch('foton_system.core.memory.vector_store.VectorStoreManager')
    def test_multi_colecao_exibe_todos_campos(self, MockVSM):
        """Deve exibir mode, collection_name, model_name, dimensions, chunks, CB, last_index."""
        mock_store = MagicMock()
        mock_store.diagnostic.return_value = {
            "mode": "dual",
            "stores": {
                "minilm": {
                    "model_tag": "minilm",
                    "model_name": "MiniLM",
                    "collection_name": "foton_minilm_384d",
                    "dimensions": 384,
                    "total_chunks": 42,
                    "circuit_breaker_status": "CLOSED",
                    "ultima_indexacao": "2026-07-03 10:00:00",
                },
                "bgem3": {
                    "model_tag": "bgem3",
                    "model_name": "BGE-M3",
                    "collection_name": "foton_bgem3_1024d",
                    "dimensions": 1024,
                    "total_chunks": 10,
                    "circuit_breaker_status": "OPEN",
                    "ultima_indexacao": "2026-07-02",
                },
            },
        }
        MockVSM.return_value = mock_store

        from foton_system.interfaces.mcp.foton_mcp import diagnostico_conhecimento
        result = diagnostico_conhecimento()

        self.assertIn("mode: dual", result)
        self.assertIn("minilm", result)
        self.assertIn("bgem3", result)
        self.assertIn("foton_minilm_384d", result)
        self.assertIn("foton_bgem3_1024d", result)
        self.assertIn("MiniLM", result)
        self.assertIn("BGE-M3", result)
        self.assertIn("384d", result)
        self.assertIn("1024d", result)
        self.assertIn("42 chunks", result)
        self.assertIn("10 chunks", result)
        self.assertIn("CLOSED", result)
        self.assertIn("OPEN", result)
        self.assertIn("2026-07-03", result)
        self.assertIn("2026-07-02", result)


class TestDiagnosticoLegado(unittest.TestCase):
    """STORY-037 AC3: Modo legado sem config rag — sem mode no output."""

    @patch('foton_system.core.memory.vector_store.VectorStoreManager')
    def test_legado_sem_mode_no_output(self, MockVSM):
        """Legado: apenas 1 colecao, sem 'mode' no texto."""
        mock_store = MagicMock()
        mock_store.diagnostic.return_value = {
            "mode": "minilm",
            "stores": {
                "minilm": {
                    "model_tag": "minilm",
                    "model_name": "MiniLM",
                    "collection_name": "foton_minilm_384d",
                    "dimensions": 384,
                    "total_chunks": 42,
                    "circuit_breaker_status": "CLOSED",
                    "ultima_indexacao": "2026-07-03",
                },
            },
        }
        MockVSM.return_value = mock_store

        from foton_system.interfaces.mcp.foton_mcp import diagnostico_conhecimento
        result = diagnostico_conhecimento()

        self.assertNotIn("mode:", result)
        self.assertIn("42 chunks", result)
        self.assertIn("CLOSED", result)


class TestDiagnosticoVazio(unittest.TestCase):
    """STORY-037 AC5: Nenhuma colecao — mensagem informativa."""

    @patch('foton_system.core.memory.vector_store.VectorStoreManager')
    def test_vazio_mensagem_informativa(self, MockVSM):
        """Sem stores — retorna mensagem informativa."""
        mock_store = MagicMock()
        mock_store.diagnostic.return_value = {
            "mode": "minilm",
            "stores": {},
        }
        MockVSM.return_value = mock_store

        from foton_system.interfaces.mcp.foton_mcp import diagnostico_conhecimento
        result = diagnostico_conhecimento()

        self.assertIn("Nenhuma coleção", result)

    @patch('foton_system.core.memory.vector_store.VectorStoreManager')
    def test_vazio_sem_stores_key(self, MockVSM):
        """stores key ausente — trata como vazio."""
        mock_store = MagicMock()
        mock_store.diagnostic.return_value = {"mode": "minilm"}
        MockVSM.return_value = mock_store

        from foton_system.interfaces.mcp.foton_mcp import diagnostico_conhecimento
        result = diagnostico_conhecimento()

        self.assertIn("Nenhuma coleção", result)


class TestDiagnosticoContrato(unittest.TestCase):
    """STORY-037 AC7: Schema da resposta nao quebra consumidores existentes."""

    @patch('foton_system.core.memory.vector_store.VectorStoreManager')
    def test_contrato_campos_essenciais_presentes(self, MockVSM):
        """Campos obrigatorios (total_chunks, cb_status, ultima_indexacao) ainda no output."""
        mock_store = MagicMock()
        mock_store.diagnostic.return_value = {
            "mode": "minilm",
            "stores": {
                "minilm": {
                    "model_tag": "minilm",
                    "model_name": "MiniLM",
                    "collection_name": "foton_minilm_384d",
                    "dimensions": 384,
                    "total_chunks": 42,
                    "circuit_breaker_status": "CLOSED",
                    "ultima_indexacao": "2026-07-02 10:00:00",
                },
            },
        }
        MockVSM.return_value = mock_store

        from foton_system.interfaces.mcp.foton_mcp import diagnostico_conhecimento
        result = diagnostico_conhecimento()

        self.assertIn("42", result)
        self.assertIn("CLOSED", result)
        self.assertIn("2026-07-02", result)


class TestDiagnosticoErro(unittest.TestCase):
    """STORY-037: Exception retorna mensagem de erro."""

    @patch('foton_system.core.memory.vector_store.VectorStoreManager')
    def test_erro_retorna_mensagem(self, MockVSM):
        """Excecao vira ❌ Diagnostic error."""
        MockVSM.side_effect = RuntimeError("chroma fail")

        from foton_system.interfaces.mcp.foton_mcp import diagnostico_conhecimento
        result = diagnostico_conhecimento()

        self.assertIn("❌ Diagnostic error", result)
        self.assertIn("chroma fail", result)


if __name__ == '__main__':
    unittest.main()
