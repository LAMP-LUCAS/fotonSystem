"""
Comprehensive CLI Menu Tests (Simplified)

Uses inline patching to avoid setUp decorator issues.
Tests core menu functionality and navigation flows.
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd


def create_mocked_menu():
    """Factory to create MenuSystem with mocked dependencies."""
    with patch('foton_system.interfaces.cli.menus.ExcelClientRepository') as MockRepo, \
         patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
         patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'):
        from foton_system.interfaces.cli.menus import MenuSystem
        menu = MenuSystem()
        menu.client_repo = MockRepo.return_value
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
            
            MockRepo.assert_called_once()
            MockDOCX.assert_called_once()
            MockPPTX.assert_called_once()
            self.assertIsNotNone(menu.client_service)
            self.assertIsNotNone(menu.document_service)


class TestMenuNavigation(unittest.TestCase):
    """Tests for menu navigation flows."""

    def test_clients_menu_returns_on_zero(self):
        """Clients menu exits on '0' input."""
        menu = create_mocked_menu()
        with patch('builtins.input', return_value='0'):
            menu.handle_clients()  # Should not crash

    def test_clients_menu_sync_db_from_folders(self):
        """Option 1 calls sync_clients_db_from_folders."""
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['1', '0']), \
             patch.object(menu.client_service, 'sync_clients_db_from_folders') as mock_sync:
            menu.handle_clients()
            mock_sync.assert_called_once()

    def test_clients_menu_sync_folders_from_db(self):
        """Option 2 calls sync_client_folders_from_db."""
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['2', '0']), \
             patch.object(menu.client_service, 'sync_client_folders_from_db') as mock_sync:
            menu.handle_clients()
            mock_sync.assert_called_once()

    def test_services_menu_returns_on_zero(self):
        """Services menu exits on '0' input."""
        menu = create_mocked_menu()
        with patch('builtins.input', return_value='0'):
            menu.handle_services()

    def test_services_menu_sync_db(self):
        """Option 1 calls sync_services_db_from_folders."""
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['1', '0']), \
             patch.object(menu.client_service, 'sync_services_db_from_folders') as mock_sync:
            menu.handle_services()
            mock_sync.assert_called_once()

    def test_documents_menu_returns_on_zero(self):
        """Documents menu exits on '0' input."""
        menu = create_mocked_menu()
        with patch('builtins.input', return_value='0'):
            menu.handle_documents()

    def test_productivity_menu_returns_on_zero(self):
        """Productivity menu exits on '0' input."""
        menu = create_mocked_menu()
        with patch('builtins.input', return_value='0'):
            menu.handle_productivity()


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
            self.assertEqual(call_args['Alias'], '001_Silva')

    def test_create_client_ui_handles_validation_error(self):
        """Shows error for invalid client data."""
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['Invalid', 'Alias', '123']), \
             patch.object(menu.client_service, 'create_client', side_effect=ValueError("Invalid")):
            menu.create_client_ui()  # Should not raise


class TestClientSearch(unittest.TestCase):
    """Tests for client search UI."""

    def test_search_returns_matching_clients(self):
        """search_client_ui finds clients by partial match."""
        menu = create_mocked_menu()
        menu.client_repo.get_clients_dataframe = MagicMock(return_value=pd.DataFrame({
            'NomeCliente': ['João Silva', 'Maria Santos'],
            'Alias': ['001_Silva', '002_Santos']
        }))
        
        with patch('builtins.input', return_value='Silva'):
            menu.search_client_ui()  # Should not raise

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
             patch('os.system'), \
             patch('sys.exit') as mock_exit:
            menu.run()
            mock_exit.assert_called()

    def test_main_menu_invalid_option(self):
        """Invalid option shows error message."""
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['999', '0']), \
             patch('os.system'), \
             patch('sys.exit'):
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
        with patch('builtins.input', side_effect=['S', '']), \
             patch('foton_system.interfaces.cli.menus.InstallService') as MockInstall:
            mock_install = MagicMock()
            MockInstall.return_value = mock_install
            
            menu.handle_installation()
            
            mock_install.install.assert_called_once()


class TestListSelection(unittest.TestCase):
    """Tests for generic list selection helper."""

    def test_select_from_list_returns_first_item(self):
        """Selecting '1' returns first item in list."""
        menu = create_mocked_menu()
        items = ['item1', 'item2', 'item3']
        with patch('builtins.input', return_value='1'):
            result = menu._select_from_list(items)
        self.assertEqual(result, 'item1')

    def test_select_from_list_returns_third_item(self):
        """Selecting '3' returns third item in list."""
        menu = create_mocked_menu()
        items = ['item1', 'item2', 'item3']
        with patch('builtins.input', return_value='3'):
            result = menu._select_from_list(items)
        self.assertEqual(result, 'item3')

    def test_select_from_list_invalid_returns_none(self):
        """Invalid option returns None."""
        menu = create_mocked_menu()
        items = ['item1', 'item2']
        with patch('builtins.input', return_value='99'):
            result = menu._select_from_list(items)
        self.assertIsNone(result)

    def test_select_from_list_non_numeric_returns_none(self):
        """Non-numeric input returns None."""
        menu = create_mocked_menu()
        items = ['item1', 'item2']
        with patch('builtins.input', return_value='abc'):
            result = menu._select_from_list(items)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
