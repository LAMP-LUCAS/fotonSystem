import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

class TestMCPRegistrarFinanceiro(unittest.TestCase):
    """Tests for registrar_financeiro tool."""

    @patch('foton_system.core.ops.op_finance_entry.OpFinanceEntry')
    def test_success_returns_auditado(self, MockOp):
        """Successful call returns message with 'Auditado'."""
        mock_op = MagicMock()
        mock_op.execute.return_value = {'message': 'Entry added successfully'}
        MockOp.return_value = mock_op
        
        from foton_system.interfaces.mcp.foton_mcp import registrar_financeiro
        
        result = registrar_financeiro('TestClient', 'Description', 100.0, 'ENTRADA')
        
        self.assertIn('Auditado', result)

    @patch('foton_system.core.ops.op_finance_entry.OpFinanceEntry')
    def test_import_error_handled(self, MockOp):
        """Errors in OP return descriptive error message."""
        MockOp.side_effect = Exception("Module not found")
        from foton_system.interfaces.mcp.foton_mcp import registrar_financeiro
        
        result = registrar_financeiro('TestClient', 'Desc', 100.0)
        
        self.assertIn('Erro', result)


class TestMCPConsultarFinanceiro(unittest.TestCase):
    """Tests for consultar_financeiro tool."""

    def test_returns_formatted_balance(self):
        """Returns properly formatted balance string."""
        with patch('foton_system.interfaces.mcp.foton_mcp._get_factory') as mock_factory:
            mock_svc = MagicMock()
            mock_svc.get_summary.return_value = MagicMock(
                success=True, total_income=1500.50, total_expenses=499.50, balance=1001.00
            )
            mock_factory.return_value.get_finance_service.return_value = mock_svc
            
            from foton_system.interfaces.mcp.foton_mcp import consultar_financeiro
            
            result = consultar_financeiro('TestClient')
            
            self.assertIn('1001.00', result)
            self.assertIn('Saldo', result)


class TestMCPListarTemplates(unittest.TestCase):
    """Tests for listar_templates tool."""

    def test_returns_pptx_and_docx_lists(self):
        """Returns both PPTX and DOCX template lists."""
        with patch('foton_system.interfaces.mcp.foton_mcp._get_factory') as mock_factory:
            mock_doc_svc = MagicMock()
            mock_doc_svc.list_templates.return_value = MagicMock(
                success=True,
                templates={'pptx': ['prop.pptx'], 'docx': ['contract.docx']}
            )
            mock_factory.return_value.get_document_service.return_value = mock_doc_svc

            from foton_system.interfaces.mcp.foton_mcp import listar_templates

            result = listar_templates()

            self.assertIn('PPTX', result)
            self.assertIn('DOCX', result)


class TestMCPGerarDocumento(unittest.TestCase):
    """Tests for gerar_documento tool."""

    @patch('foton_system.core.ops.op_doc_gen.OpGenerateDocument')
    def test_success_returns_path(self, MockOp):
        """Successful generation returns output path."""
        mock_op = MagicMock()
        mock_op.execute.return_value = {'output_path': '/path/to/document.docx'}
        MockOp.return_value = mock_op
        
        from foton_system.interfaces.mcp.foton_mcp import gerar_documento
        
        result = gerar_documento('TestClient', 'template.docx', {})
        
        self.assertIn('document.docx', result)
        self.assertIn('Auditado', result)

    @patch('foton_system.core.ops.op_doc_gen.OpGenerateDocument')
    def test_error_returns_message(self, MockOp):
        """Errors return descriptive message."""
        MockOp.side_effect = Exception("Gen failed")
        from foton_system.interfaces.mcp.foton_mcp import gerar_documento
        result = gerar_documento('TestClient', 'template.docx')
        self.assertIn('Erro POP', result)


class TestMCPGetClientPath(unittest.TestCase):
    """Tests for client path resolution proxy."""

    def test_returns_existing_path(self):
        """Proxies resolution to client service."""
        with patch('foton_system.interfaces.mcp.foton_mcp._get_factory') as mock_factory:
            mock_svc = MagicMock()
            mock_svc.resolve_client_path.return_value = Path("/base/CLIENTE")
            mock_factory.return_value.get_client_service.return_value = mock_svc
            
            from foton_system.interfaces.mcp.foton_mcp import _resolve_client_path
            result = _resolve_client_path(Path("/base"), "CLIENTE", MagicMock())
            self.assertEqual(result, Path("/base/CLIENTE"))


class TestMCPConsultarConhecimento(unittest.TestCase):
    """Tests for semantic search tool."""

    @patch('foton_system.core.ops.op_query_knowledge.OpQueryKnowledge')
    def test_empty_results_returns_message(self, MockOp):
        """Empty results return appropriate message."""
        mock_op = MagicMock()
        mock_op.execute.return_value = {"status": "EMPTY"}
        MockOp.return_value = mock_op
        
        from foton_system.interfaces.mcp.foton_mcp import consultar_conhecimento
        result = consultar_conhecimento("test")
        self.assertIn('No relevant knowledge found', result)

if __name__ == '__main__':
    unittest.main()
