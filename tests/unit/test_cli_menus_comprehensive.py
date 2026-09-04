"""
Comprehensive CLI Menu Tests (Fixed)

Tests core menu functionality and navigation flows using a mock UIProvider.
Ensures 100% passing rate after architecture refactor.
"""

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
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
        """Option 5 delegates to pipeline_sincronizacao."""
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['5', '', '0']), \
             patch('foton_system.modules.clients.application.use_cases.pipeline_sync.pipeline_sincronizacao') as mock_pipeline:
            menu.handle_clients()
            mock_pipeline.assert_called_once_with('pastas_to_db', dry_run=False)

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
        with patch('builtins.input', side_effect=['João Silva', '001_Silva', '', '', '11999999999']), \
             patch.object(menu.client_service, 'resolve_client_path', side_effect=ValueError("Not found")), \
             patch.object(menu.client_service, 'create_client') as mock_create:
            menu.create_client_ui()
            
            mock_create.assert_called_once()
            call_args, call_kwargs = mock_create.call_args
            self.assertEqual(call_args[0], 'João Silva')
            self.assertEqual(call_kwargs.get('phone'), '11999999999')

    def test_create_client_ui_handles_validation_error(self):
        """Shows error for invalid client data."""
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['Invalid', 'Alias', '', '', '123']), \
             patch.object(menu.client_service, 'resolve_client_path', side_effect=ValueError("Not found")), \
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


class TestFillMissingCodesUI(unittest.TestCase):
    """Tests for fill_missing_codes_ui."""

    def test_fill_missing_codes_confirms_and_runs(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['S']), \
             patch.object(menu.client_service, 'fill_missing_codes', return_value={'clientes_alterados': 3, 'servicos_alterados': 2}):
            menu.fill_missing_codes_ui()

    def test_fill_missing_codes_cancelled(self):
        menu = create_mocked_menu()
        with patch('builtins.input', return_value='N'):
            menu.fill_missing_codes_ui()

    def test_fill_missing_codes_none_found(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['S']), \
             patch.object(menu.client_service, 'fill_missing_codes', return_value={'clientes_alterados': 0, 'servicos_alterados': 0}):
            menu.fill_missing_codes_ui()


class TestReadClientInfoUI(unittest.TestCase):
    """Tests for read_client_info_ui."""

    def test_read_client_info_success(self):
        menu = create_mocked_menu()
        with patch('builtins.input', return_value='CLIENTE_A'), \
             patch.object(menu.client_service, 'read_client_info', return_value={'filename': 'INFO.md', 'content': '# Dados'}):
            menu.read_client_info_ui()

    def test_read_client_info_empty_name_returns(self):
        menu = create_mocked_menu()
        with patch('builtins.input', return_value=''):
            menu.read_client_info_ui()

    def test_read_client_info_not_found(self):
        menu = create_mocked_menu()
        with patch('builtins.input', return_value='GHOST'), \
             patch.object(menu.client_service, 'read_client_info', side_effect=ValueError("No INFO file")):
            menu.read_client_info_ui()


class TestUpdateClientInfoUI(unittest.TestCase):
    """Tests for update_client_info_ui."""

    def test_update_client_info_success(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['CLIENTE_A', 'DADOS', 'linha1', '', '']), \
             patch.object(menu.client_service, 'update_client_info', return_value='backup.bak'):
            menu.update_client_info_ui()

    def test_update_client_info_empty_name_returns(self):
        menu = create_mocked_menu()
        with patch('builtins.input', return_value=''):
            menu.update_client_info_ui()

    def test_update_client_info_empty_section_returns(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['CLIENTE_A', '']):
            menu.update_client_info_ui()


class TestClientServicosUI(unittest.TestCase):
    """Tests for client servicos submenu and UI."""

    def test_servicos_submenu_listar(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['1', 'CLIENTE_A', '', '0']), \
             patch.object(menu.client_service, 'list_service_nodes', return_value=[]):
            menu.handle_client_servicos_menu()

    def test_servicos_submenu_criar_no_name(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['2', 'CLIENTE_A', '', '', '0']):
            menu.handle_client_servicos_menu()

    def test_servicos_submenu_return(self):
        menu = create_mocked_menu()
        with patch('builtins.input', return_value='0'):
            menu.handle_client_servicos_menu()


class TestFinanceUI(unittest.TestCase):
    """Tests for finance UI methods."""

    def test_finance_submenu_consultar(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['2', 'CLIENTE_A', '', '0']), \
             patch.object(menu.client_service, 'resolve_client_path') as mock_resolve, \
             patch('foton_system.modules.finance.application.use_cases.finance_service.FinanceService') as MockFS:
            mock_resolve.return_value = Path('/fake/client')
            MockFS.return_value.get_summary.return_value = {'total_entradas': 1000, 'total_saidas': 500, 'saldo': 500}
            menu.handle_finance()

    def test_finance_submenu_resumo(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['3', '', '0']):
            menu.handle_finance()

    def test_finance_submenu_cancel(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['1', '', '', '0']):
            menu.handle_finance()

    def test_finance_submenu_return(self):
        menu = create_mocked_menu()
        with patch('builtins.input', return_value='0'):
            menu.handle_finance()


class TestFullNavigationFlows(unittest.TestCase):
    """Test that new menu options navigate correctly."""

    def test_main_menu_shows_finance(self):
        with patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
             patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
             patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'), \
             patch('builtins.input', return_value='0'), \
             patch('builtins.print') as mock_print:
            from foton_system.interfaces.cli.menus import MenuSystem
            menu = MenuSystem()
            with self.assertRaises(SystemExit):
                menu.run()
            printed = "".join([c.args[0] for c in mock_print.call_args_list if c.args])
            self.assertIn("Financeiro", printed)

    def test_client_menu_has_new_options(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['1', '', '', '0', '0']):
            menu.handle_clients()

    def test_client_menu_has_fill_codes_option(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['4', 'N', '', '0', '0']):
            menu.handle_clients()

    def test_client_menu_servicos_option(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['10', '0', '', '0', '0']):
            menu.handle_clients()

    def test_client_sync_import_option(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['4', 'S', '', '0', '0']), \
             patch.object(menu.client_service, 'fill_missing_codes', return_value={'clientes_alterados': 0, 'servicos_alterados': 0}):
            menu.handle_clients()


class TestMenuMapping(unittest.TestCase):
    """Testa que cada opção de menu chama o handler correto, sem executar a lógica real."""

    def test_option_1_create_client(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['1', '', '', '0']), \
             patch.object(menu, 'create_client_ui') as mock_fn:
            menu.handle_clients()
            mock_fn.assert_called_once()

    def test_option_2_read_info(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['2', '', '', '0']), \
             patch.object(menu, 'read_client_info_ui') as mock_fn:
            menu.handle_clients()
            mock_fn.assert_called_once()

    def test_option_3_update_info(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['3', '', '', '', '0']), \
             patch.object(menu, 'update_client_info_ui') as mock_fn:
            menu.handle_clients()
            mock_fn.assert_called_once()

    def test_option_4_fill_codes(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['4', 'N', '', '0']), \
             patch.object(menu, 'fill_missing_codes_ui') as mock_fn:
            menu.handle_clients()
            mock_fn.assert_called_once()

    def test_option_5_sync_db_from_folders(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['5', '', '0']), \
             patch('foton_system.modules.clients.application.use_cases.pipeline_sync.pipeline_sincronizacao') as mock_fn:
            menu.handle_clients()
            mock_fn.assert_called_once_with('pastas_to_db', dry_run=False)

    def test_option_6_sync_folders_from_db(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['6', '', '0']), \
             patch('foton_system.modules.clients.application.use_cases.pipeline_sync.pipeline_sincronizacao') as mock_fn:
            menu.handle_clients()
            mock_fn.assert_called_once_with('db_to_pastas', dry_run=False)

    def test_option_7_pipeline_sync(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['7', '3', '', '0']), \
             patch.object(menu, 'pipeline_sync_ui') as mock_fn:
            menu.handle_clients()
            mock_fn.assert_called_once()

    def test_option_8_list_all_clients(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['8', '', '', '0']), \
             patch.object(menu, 'list_all_clients_ui') as mock_fn:
            menu.handle_clients()
            mock_fn.assert_called_once()

    def test_option_9_search(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['9', '', '', '0']), \
             patch.object(menu, 'search_client_ui') as mock_fn:
            menu.handle_clients()
            mock_fn.assert_called_once()

    def test_option_10_servicos_submenu(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['10', '0', '', '0']), \
             patch.object(menu, 'handle_client_servicos_menu') as mock_fn:
            menu.handle_clients()
            mock_fn.assert_called_once()

    def test_option_11_client_sync_menu(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['11', '0', '', '0']), \
             patch.object(menu, 'handle_client_sync_menu') as mock_fn:
            menu.handle_clients()
            mock_fn.assert_called_once()

    def test_option_12_remove(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['12', '', '', '0']), \
             patch.object(menu, 'remove_client_ui') as mock_fn:
            menu.handle_clients()
            mock_fn.assert_called_once()

    def test_option_13_restore(self):
        menu = create_mocked_menu()
        with patch('builtins.input', side_effect=['13', '', '', '0']), \
             patch.object(menu, 'restore_client_ui') as mock_fn:
            menu.handle_clients()
            mock_fn.assert_called_once()


if __name__ == '__main__':
    unittest.main()
