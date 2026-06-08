"""
Tests for path traversal prevention in MCP tools.
"""

import logging
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from pathlib import Path

logging.disable(logging.CRITICAL)


class TestPathSanitizationPrinciple(unittest.TestCase):
    """Core path sanitization must prevent directory traversal."""

    def test_path_name_extraction_strips_unix_traversal(self):
        """Path(name).name strips '../../etc/passwd' to just 'passwd'."""
        self.assertEqual(Path("../../etc/passwd").name, "passwd")

    def test_path_name_extraction_strips_windows_traversal(self):
        """Path(name).name strips '..\\..\\secret' to just 'secret'."""
        self.assertEqual(Path("..\\..\\secret").name, "secret")

    def test_normal_name_preserved(self):
        """Path(name).name keeps normal filenames intact."""
        self.assertEqual(Path("contrato.docx").name, "contrato.docx")

    def test_normalize_client_name_strips_unix_traversal(self):
        """normalize_client_name sanitizes '../../evil' to 'EVIL'."""
        from foton_system.modules.clients.application.use_cases.client_validation import normalize_client_name
        self.assertEqual(normalize_client_name("../../evil"), "EVIL")

    def test_normalize_client_name_strips_windows_traversal(self):
        """normalize_client_name sanitizes '..\\..\\secret' to 'SECRET'."""
        from foton_system.modules.clients.application.use_cases.client_validation import normalize_client_name
        self.assertEqual(normalize_client_name("..\\..\\secret"), "SECRET")


class TestPathTraversalValidarTemplate(unittest.TestCase):
    """validar_template must sanitize path traversal in nome_template."""

    def test_unix_path_traversal_not_in_result(self):
        """../../etc/passwd should not appear in the result path."""
        with patch('foton_system.interfaces.mcp.foton_mcp.Path.exists', return_value=False):
            with patch('foton_system.interfaces.mcp.foton_mcp._get_config') as mock_config:
                mock_cfg = MagicMock()
                mock_cfg.templates_path = Path("/nonexistent/templates")
                mock_config.return_value = mock_cfg

                with patch('foton_system.interfaces.mcp.foton_mcp._get_factory') as mock_factory:
                    mock_svc = MagicMock()
                    mock_svc.resolve_client_path.return_value = Path("/nonexistent/clientes/TEST")
                    mock_factory.return_value.get_client_service.return_value = mock_svc

                    from foton_system.interfaces.mcp.foton_mcp import validar_template
                    result = validar_template("TEST", "../../etc/passwd")

                    self.assertNotIn("/etc/passwd", result)

    def test_windows_path_traversal_not_in_result(self):
        """..\\..\\..\\secret should not appear in the result path."""
        with patch('foton_system.interfaces.mcp.foton_mcp.Path.exists', return_value=False):
            with patch('foton_system.interfaces.mcp.foton_mcp._get_config') as mock_config:
                mock_cfg = MagicMock()
                mock_cfg.templates_path = Path("/templates")
                mock_config.return_value = mock_cfg

                with patch('foton_system.interfaces.mcp.foton_mcp._get_factory') as mock_factory:
                    mock_svc = MagicMock()
                    mock_svc.resolve_client_path.return_value = Path("/clientes/TEST")
                    mock_factory.return_value.get_client_service.return_value = mock_svc

                    from foton_system.interfaces.mcp.foton_mcp import validar_template
                    result = validar_template("TEST", "..\\..\\..\\secret")

                    self.assertNotIn("..\\..\\..\\secret", result)
                    self.assertIn("not found", result.lower())


class TestPathTraversalCadastrarCliente(unittest.TestCase):
    """cadastrar_cliente must sanitize names with path components."""

    @patch('foton_system.core.ops.op_create_client.OpCreateClient')
    def test_unix_path_traversal_uses_normalized_name(self, MockOp):
        """../../evil becomes EVIL — normalized name is used."""
        mock_op = MagicMock()
        mock_op.execute.return_value = {
            'client_path': '/base/EVIL',
            'client_id': 'EVIL_001'
        }
        MockOp.return_value = mock_op

        from foton_system.interfaces.mcp.foton_mcp import cadastrar_cliente
        result = cadastrar_cliente("../../evil")

        self.assertIn("Nome normalizado: EVIL", result)

    @patch('foton_system.core.ops.op_create_client.OpCreateClient')
    def test_windows_path_traversal_sanitized(self, MockOp):
        """..\\..\\..\\secret becomes SECRET."""
        mock_op = MagicMock()
        mock_op.execute.return_value = {
            'client_path': '/base/SECRET',
            'client_id': 'SECRET_001'
        }
        MockOp.return_value = mock_op

        from foton_system.interfaces.mcp.foton_mcp import cadastrar_cliente
        result = cadastrar_cliente("..\\..\\..\\secret")

        self.assertIn("Nome normalizado: SECRET", result)


class TestPathTraversalLerFichaCliente(unittest.TestCase):
    """ler_ficha_cliente must reject invalid client names."""

    def test_unknown_client_returns_error(self):
        """Error returned for non-existent client."""
        with patch('foton_system.interfaces.mcp.foton_mcp._get_factory') as mock_factory:
            mock_svc = MagicMock()
            mock_svc.read_client_info.side_effect = ValueError("Client not found")
            mock_factory.return_value.get_client_service.return_value = mock_svc

            from foton_system.interfaces.mcp.foton_mcp import ler_ficha_cliente
            result = ler_ficha_cliente("nonexistent_client")

            self.assertIn("Client not found", result)


if __name__ == '__main__':
    unittest.main()
