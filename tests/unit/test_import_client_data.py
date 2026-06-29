import unittest
from unittest.mock import MagicMock, patch, call
import pandas as pd
import tempfile
from pathlib import Path


class TestImportClientDataDomain(unittest.TestCase):
    """Tests for import_client_data() in client_crud domain layer."""

    def setUp(self):
        self.repo = MagicMock()
        self.config = MagicMock()
        self.config.base_pasta_clientes = Path(tempfile.mkdtemp())
        self.config.ignored_folders = []

    @patch('foton_system.modules.clients.application.use_cases.client_crud._get_latest_file')
    @patch('foton_system.modules.clients.application.use_cases.client_crud._read_file_content')
    def test_import_client_data_imports_new_clients(self, mock_read, mock_latest):
        from foton_system.modules.clients.application.use_cases.client_crud import import_client_data
        self.repo.get_clients_dataframe.return_value = pd.DataFrame(columns=['Alias', 'NomeCliente'])
        self.repo.list_client_folders.return_value = {'CLIENTE_A'}
        mock_latest.return_value = Path('/fake/INFO-CLIENTE.md')
        mock_read.return_value = {'NomeCliente': 'Joao', 'Telefone': '123'}
        import_client_data(self.repo, self.config)
        self.repo.save_clients.assert_called_once()

    @patch('foton_system.modules.clients.application.use_cases.client_crud._get_latest_file')
    @patch('foton_system.modules.clients.application.use_cases.client_crud._read_file_content')
    def test_import_client_data_skips_when_no_change(self, mock_read, mock_latest):
        from foton_system.modules.clients.application.use_cases.client_crud import import_client_data
        df = pd.DataFrame({'Alias': ['CLIENTE_A'], 'NomeCliente': ['Joao']})
        self.repo.get_clients_dataframe.return_value = df
        self.repo.list_client_folders.return_value = {'CLIENTE_A'}
        mock_latest.return_value = Path('/fake/INFO-CLIENTE.md')
        mock_read.return_value = {}
        import_client_data(self.repo, self.config)
        self.repo.save_clients.assert_not_called()

    @patch('foton_system.modules.clients.application.use_cases.client_crud._get_latest_file')
    def test_import_client_data_skips_client_without_info_file(self, mock_latest):
        from foton_system.modules.clients.application.use_cases.client_crud import import_client_data
        self.repo.get_clients_dataframe.return_value = pd.DataFrame(columns=['Alias', 'NomeCliente'])
        self.repo.list_client_folders.return_value = {'CLIENTE_A'}
        mock_latest.return_value = None
        import_client_data(self.repo, self.config)
        self.repo.save_clients.assert_not_called()

    def test_import_client_data_empty_folder_returns_early(self):
        from foton_system.modules.clients.application.use_cases.client_crud import import_client_data
        self.repo.get_clients_dataframe.return_value = pd.DataFrame(columns=['Alias', 'NomeCliente'])
        self.repo.list_client_folders.return_value = set()
        import_client_data(self.repo, self.config)
        self.repo.save_clients.assert_not_called()


class TestImportClientDataService(unittest.TestCase):
    """Tests for ClientService.import_client_data() wrapper."""

    def test_service_wrapper_delegates_to_crud(self):
        from foton_system.modules.clients.application.use_cases.client_service import ClientService
        repo = MagicMock()
        service = ClientService(repo)
        with patch('foton_system.modules.clients.application.use_cases.client_service.client_crud.import_client_data') as mock:
            service.import_client_data()
            mock.assert_called_once_with(repo, service._config)


class TestImportClientDataMCP(unittest.TestCase):
    """Tests for MCPClientService.import_client_data()."""

    def test_mcp_service_delegates_and_returns_message(self):
        from foton_system.interfaces.mcp.mcp_services import MCPClientService
        domain = MagicMock()
        mcp = MCPClientService(domain)
        result = mcp.import_client_data()
        domain.import_client_data.assert_called_once()
        self.assertIn("Client data imported", result)



class TestImportClientDataMCPTool(unittest.TestCase):
    """Tests for the MCP tool importar_dados_clientes."""

    def test_tool_delegates_to_service(self):
        with patch('foton_system.interfaces.mcp.foton_mcp._get_factory') as mock_factory:
            mock_svc = MagicMock()
            mock_svc.import_client_data.return_value = "Client data imported from files."
            mock_factory.return_value.get_client_service.return_value = mock_svc
            from foton_system.interfaces.mcp.foton_mcp import importar_dados_clientes
            result = importar_dados_clientes()
            mock_svc.import_client_data.assert_called_once()
            self.assertIn("✅", result)

    def test_tool_error_returns_error_message(self):
        with patch('foton_system.interfaces.mcp.foton_mcp._get_factory') as mock_factory:
            mock_svc = MagicMock()
            mock_svc.import_client_data.side_effect = Exception("DB error")
            mock_factory.return_value.get_client_service.return_value = mock_svc
            from foton_system.interfaces.mcp.foton_mcp import importar_dados_clientes
            result = importar_dados_clientes()
            self.assertIn("❌", result)


class TestImportClientDataNavigation(unittest.TestCase):
    """Test that TUI menu routes to import_client_data."""

    def test_client_sync_menu_calls_import(self):
        with patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
             patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
             patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'):
            from foton_system.interfaces.cli.menus import MenuSystem
            menu = MenuSystem()
            with patch('builtins.input', side_effect=['2', '', '0']), \
                 patch.object(menu.client_service, 'import_client_data') as mock_import:
                menu.handle_client_sync_menu()
                mock_import.assert_called_once()


if __name__ == '__main__':
    unittest.main()
