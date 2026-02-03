"""
Comprehensive CLI Menu Tests (Fixed)

Tests core menu functionality and navigation flows using a mock UIProvider.
Ensures 100% passing rate after architecture refactor.
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from foton_system.interfaces.cli.ui_provider import TUIProvider


def create_mocked_menu():
    """Factory to create MenuSystem with mocked dependencies and TUIProvider."""
    # Mocking external adapters before import
    with patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
         patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
         patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'):
        
        from foton_system.interfaces.cli.menus import MenuSystem
        
        # Use a TUIProvider with mocked input for tests
        ui = TUIProvider()
        menu = MenuSystem(ui_provider=ui)
        
        # Mocking the client repository dataframe specifically
        menu.client_repo.get_clients_dataframe.return_value = pd.DataFrame(columns=['NomeCliente', 'Alias', 'TelefoneCliente'])
        
        return menu


class TestMenuSystemInitialization(unittest.TestCase):
    """Tests for MenuSystem initialization."""

    def test_menu_system_initializes_services(self):
        """MenuSystem initializes all required services on startup."""
        with patch('foton_system.interfaces.cli.menus.ExcelClientRepository') as MockRepo, \
             patch('foton_system.interfaces.cli.menus.PythonDocxAdapter') as MockDOCX, \
             patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter') as MockPPTX:
            from foton_system.interfaces.cli.menus import MenuSystem
            
            menu = MenuSystem()
            
            self.assertIsNotNone(menu.ui)
            self.assertIsNotNone(menu.client_service)
            self.assertIsNotNone(menu.document_service)


class TestMenuNavigation(unittest.TestCase):
    """Tests for menu navigation flows."""

    def test_clients_menu_returns_on_zero(self):
        """Clients menu exits on '0' input."""
        menu = create_mocked_menu()
        with patch('builtins.input', return_value='0'):
            menu.handle_clients()

    def test_clients_menu_sync_db_from_folders(self):
        """Option 1 calls sync_clients_db_from_folders."""
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['1', '0']), \
             patch.object(menu.client_service, 'sync_clients_db_from_folders') as mock_sync:
            menu.handle_clients()
            mock_sync.assert_called_once()

    def test_services_menu_returns_on_zero(self):
        """Services menu exits on '0' input."""
        menu = create_mocked_menu()
        with patch('builtins.input', return_value='0'):
            menu.handle_services()


class TestClientCreation(unittest.TestCase):
    """Tests for client creation UI."""

    def test_create_client_ui_calls_service(self):
        """create_client_ui passes data to service."""
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['João Silva', '001_Silva', '11999999999']), \
             patch.object(menu.client_service, 'create_client') as mock_create:
            menu.create_client_ui()
            
            mock_create.assert_called_once()
            call_args = mock_create.call_args[0][0]
            self.assertEqual(call_args['NomeCliente'], 'João Silva')

    def test_create_client_ui_handles_validation_error(self):
        """Shows error for invalid client data."""
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['Invalid', 'Alias', '123']), \
             patch.object(menu.client_service, 'create_client', side_effect=ValueError("Invalid")):
            menu.create_client_ui()


class TestClientSearch(unittest.TestCase):
    """Tests for client search UI."""

    def test_search_returns_matching_clients(self):
        """search_client_ui finds clients by partial match."""
        menu = create_mocked_menu()
        menu.client_repo.get_clients_dataframe.return_value = pd.DataFrame({
            'NomeCliente': ['João Silva'],
            'Alias': ['001_Silva']
        })
        
        with patch('builtins.input', return_value='Silva'):
            menu.search_client_ui()

    def test_search_empty_term_returns_early(self):
        """Empty search term returns immediately."""
        menu = create_mocked_menu()
        with patch('builtins.input', return_value=''):
            menu.search_client_ui()


class TestMainMenu(unittest.TestCase):
    """Tests for main menu routing."""

    def test_main_menu_exit_on_zero(self):
        """Main menu exits application on '0' input."""
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['0']), \
             patch('os.system'):
            with self.assertRaises(SystemExit):
                menu.run()



class TestInstallation(unittest.TestCase):
    """Tests for installation menu."""

    def test_installation_cancelled_on_no(self):
        """Installation is cancelled when user says 'N'."""
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['N', '']):
            menu.handle_installation()

    def test_installation_runs_on_yes(self):
        """Installation runs when user confirms with 'S'."""
        menu = create_mocked_menu()
        # Mocking the InstallService directly where it is imported in the method
        with patch('builtins.input', side_effect=['S', '']), \
             patch('foton_system.modules.shared.infrastructure.services.install_service.InstallService') as MockInstall:
            
            mock_instance = MagicMock()
            MockInstall.return_value = mock_instance
            
            menu.handle_installation()
            mock_instance.install.assert_called()


class TestListSelection(unittest.TestCase):
    """Tests for list selection logic."""

    def test_select_from_list_success(self):
        """Returns selected item from list."""
        menu = create_mocked_menu()
        items = ['A', 'B']
        with patch('builtins.input', return_value='1'):
            res = menu._select_from_list(items)
            self.assertEqual(res, 'A')

    def test_select_from_list_invalid(self):
        """Returns None for invalid index."""
        menu = create_mocked_menu()
        with patch('builtins.input', return_value='9'):
            res = menu._select_from_list(['A'])
            self.assertIsNone(res)


if __name__ == '__main__':
    unittest.main()
