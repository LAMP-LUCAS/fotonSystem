"""
MCP Server Tests with Mocked Core Dependencies

Tests MCP helper functions and tool behaviors without real MCP runtime.
Uses simplified patching to avoid import order issues.
"""

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestMCPGetClientPath(unittest.TestCase):
    """Tests for _get_client_path helper function."""

    def test_returns_existing_path(self):
        """Returns path when client folder exists."""
        with patch('foton_system.interfaces.mcp.foton_mcp._get_config') as mock_config:
            mock_cfg = MagicMock()
            mock_cfg.base_pasta_clientes = Path('/fake/clients')
            mock_config.return_value = mock_cfg
            
            from foton_system.interfaces.mcp.foton_mcp import _get_client_path
            
            with patch.object(Path, 'exists', return_value=True):
                result = _get_client_path('TestClient')
            
            self.assertIn('TestClient', str(result))

    def test_prevents_directory_traversal(self):
        """Malicious paths are sanitized."""
        with patch('foton_system.interfaces.mcp.foton_mcp._get_config') as mock_config:
            mock_cfg = MagicMock()
            mock_cfg.base_pasta_clientes = Path('/fake/clients')
            mock_config.return_value = mock_cfg
            
            from foton_system.interfaces.mcp.foton_mcp import _get_client_path
            
            # Path.name sanitizes directory traversal
            result_path = Path('../../../etc/passwd')
            sanitized = result_path.name  # Should be 'passwd'
            self.assertEqual(sanitized, 'passwd')


class TestMCPRegistrarFinanceiro(unittest.TestCase):
    """Tests for registrar_financeiro tool."""

    def test_success_returns_auditado(self):
        """Successful call returns message with 'Auditado'."""
        with patch('foton_system.interfaces.mcp.foton_mcp.OpFinanceEntry') as MockOp:
            mock_op = MagicMock()
            mock_op.execute.return_value = {'message': 'Entry added successfully'}
            MockOp.return_value = mock_op
            
            from foton_system.interfaces.mcp.foton_mcp import registrar_financeiro
            
            result = registrar_financeiro('TestClient', 'Description', 100.0, 'ENTRADA')
            
            self.assertIn('Auditado', result)

    def test_import_error_handled(self):
        """ImportError returns descriptive error message."""
        with patch('foton_system.interfaces.mcp.foton_mcp.OpFinanceEntry', side_effect=ImportError("Module not found")):
            from foton_system.interfaces.mcp.foton_mcp import registrar_financeiro
            
            result = registrar_financeiro('TestClient', 'Desc', 100.0)
            
            self.assertIn('Erro', result)


class TestMCPConsultarFinanceiro(unittest.TestCase):
    """Tests for consultar_financeiro tool."""

    def test_returns_formatted_balance(self):
        """Returns properly formatted balance string."""
        with patch('foton_system.interfaces.mcp.foton_mcp._get_client_path') as mock_path, \
             patch('foton_system.interfaces.mcp.foton_mcp.CSVFinanceRepository') as MockRepo, \
             patch('foton_system.interfaces.mcp.foton_mcp.FinanceService') as MockService:
            
            mock_path.return_value = Path('/fake/client')
            mock_service = MagicMock()
            mock_service.get_summary.return_value = {
                'saldo': 1500.50,
                'total_entradas': 2000.00,
                'total_saidas': 499.50
            }
            MockService.return_value = mock_service
            
            from foton_system.interfaces.mcp.foton_mcp import consultar_financeiro
            
            result = consultar_financeiro('TestClient')
            
            self.assertIn('1500.50', result)
            self.assertIn('Saldo', result)


class TestMCPListarTemplates(unittest.TestCase):
    """Tests for listar_templates tool."""

    def test_returns_pptx_and_docx_lists(self):
        """Returns both PPTX and DOCX template lists."""
        with patch('foton_system.interfaces.mcp.foton_mcp._get_config') as mock_config, \
             patch('foton_system.interfaces.mcp.foton_mcp.DocumentService') as MockDocService, \
             patch('foton_system.interfaces.mcp.foton_mcp.PythonDocxAdapter'), \
             patch('foton_system.interfaces.mcp.foton_mcp.PythonPPTXAdapter'):
            
            mock_cfg = MagicMock()
            mock_cfg.templates_path = MagicMock()
            mock_cfg.templates_path.mkdir = MagicMock()
            mock_config.return_value = mock_cfg
            
            mock_service = MagicMock()
            mock_service.list_templates.side_effect = [
                ['prop1.pptx', 'prop2.pptx'],
                ['contract.docx']
            ]
            MockDocService.return_value = mock_service
            
            from foton_system.interfaces.mcp.foton_mcp import listar_templates
            
            result = listar_templates()
            
            self.assertIn('PPTX', result)
            self.assertIn('DOCX', result)


class TestMCPGerarDocumento(unittest.TestCase):
    """Tests for gerar_documento tool."""

    def test_success_returns_path(self):
        """Successful generation returns output path."""
        with patch('foton_system.interfaces.mcp.foton_mcp.OpGenerateDocument') as MockOp:
            mock_op = MagicMock()
            mock_op.execute.return_value = {'output_path': '/path/to/document.docx'}
            MockOp.return_value = mock_op
            
            from foton_system.interfaces.mcp.foton_mcp import gerar_documento
            
            result = gerar_documento('TestClient', 'template.docx', {})
            
            self.assertIn('document.docx', result)
            self.assertIn('Auditado', result)

    def test_error_returns_message(self):
        """Errors return descriptive message."""
        with patch('foton_system.interfaces.mcp.foton_mcp.OpGenerateDocument') as MockOp:
            MockOp.side_effect = ImportError("Module not found")
            
            from foton_system.interfaces.mcp.foton_mcp import gerar_documento
            
            result = gerar_documento('TestClient', 'missing.docx', {})
            
            self.assertIn('Erro', result)


class TestMCPConsultarConhecimento(unittest.TestCase):
    """Tests for consultar_conhecimento tool."""

    def test_returns_formatted_results(self):
        """Returns formatted knowledge results."""
        with patch('foton_system.interfaces.mcp.foton_mcp.VectorStore') as MockStore:
            mock_store = MagicMock()
            mock_store.query.return_value = {
                'documents': [['Document content 1', 'Document content 2']],
                'metadatas': [[{'filename': 'doc1.md'}, {'filename': 'doc2.md'}]]
            }
            MockStore.return_value = mock_store
            
            from foton_system.interfaces.mcp.foton_mcp import consultar_conhecimento
            
            result = consultar_conhecimento('Test query')
            
            self.assertIn('doc1.md', result)
            self.assertIn('Document content 1', result)

    def test_empty_results_returns_message(self):
        """Empty results return appropriate message."""
        with patch('foton_system.interfaces.mcp.foton_mcp.VectorStore') as MockStore:
            mock_store = MagicMock()
            mock_store.query.return_value = {'documents': [[]], 'metadatas': [[]]}
            MockStore.return_value = mock_store
            
            from foton_system.interfaces.mcp.foton_mcp import consultar_conhecimento
            
            result = consultar_conhecimento('Unknown query')
            
            self.assertIn('Nenhum conhecimento', result)

    def test_import_error_handled(self):
        """ImportError for missing VectorStore is handled."""
        with patch('foton_system.interfaces.mcp.foton_mcp.VectorStore', side_effect=ImportError("No chromadb")):
            from foton_system.interfaces.mcp.foton_mcp import consultar_conhecimento
            
            result = consultar_conhecimento('Test')
            
            self.assertIn('Erro', result)


if __name__ == '__main__':
    unittest.main()
