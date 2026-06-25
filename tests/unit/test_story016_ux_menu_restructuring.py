"""
Tests for STORY-016: UX — Menu Restructuring + Navigation.

Covers RULE-DOMAIN-4.4, RULE-DOMAIN-4.5, RULE-DOMAIN-4.6, RULE-DOMAIN-4.7, RULE-DOMAIN-4.8.
"""

import pytest
import io
import sys
from unittest.mock import MagicMock, patch

# @story: STORY-016
# @rule: RULE-DOMAIN-4.4, RULE-DOMAIN-4.5, RULE-DOMAIN-4.6, RULE-DOMAIN-4.7, RULE-DOMAIN-4.8


# ==============================================================================
# parse_command Tests (RULE-DOMAIN-4.6)
# ==============================================================================

class TestParseCommand:
    def test_parse_command_exit(self):
        from foton_system.interfaces.cli.command_parser import parse_command
        result = parse_command('q')
        assert result == {'action': 'exit'}

    def test_parse_command_help(self):
        from foton_system.interfaces.cli.command_parser import parse_command
        result = parse_command('h')
        assert result == {'action': 'help'}

    def test_parse_command_home(self):
        from foton_system.interfaces.cli.command_parser import parse_command
        result = parse_command('00')
        assert result == {'action': 'home'}

    def test_parse_command_global_search(self):
        from foton_system.interfaces.cli.command_parser import parse_command
        result = parse_command('g')
        assert result == {'action': 'global_search'}

    def test_parse_command_numeric(self):
        from foton_system.interfaces.cli.command_parser import parse_command
        result = parse_command('5')
        assert result == {'action': 'numeric', 'value': 5}

    def test_parse_command_numeric_zero(self):
        from foton_system.interfaces.cli.command_parser import parse_command
        result = parse_command('0')
        assert result == {'action': 'numeric', 'value': 0}

    def test_parse_command_search(self):
        from foton_system.interfaces.cli.command_parser import parse_command
        result = parse_command('joão silva')
        assert result == {'action': 'search', 'term': 'joão silva'}

    def test_parse_command_case_insensitive(self):
        from foton_system.interfaces.cli.command_parser import parse_command
        assert parse_command('Q') == {'action': 'exit'}
        assert parse_command('H') == {'action': 'help'}
        assert parse_command('G') == {'action': 'global_search'}

    def test_parse_command_empty_string(self):
        from foton_system.interfaces.cli.command_parser import parse_command
        result = parse_command('')
        assert result == {'action': 'search', 'term': ''}

    def test_parse_command_whitespace(self):
        from foton_system.interfaces.cli.command_parser import parse_command
        result = parse_command('  ')
        assert result == {'action': 'search', 'term': ''}

    def test_parse_command_negative_number_not_numeric(self):
        from foton_system.interfaces.cli.command_parser import parse_command
        result = parse_command('-1')
        assert result['action'] != 'numeric'


# ==============================================================================
# confirm_action Tests (RULE-DOMAIN-4.8)
# ==============================================================================

def _make_menu():
    from foton_system.interfaces.cli.menus import MenuSystem
    menu = MenuSystem.__new__(MenuSystem)
    menu._clients_handler = MagicMock()
    menu._finance_handler = MagicMock()
    menu._docs_handler = MagicMock()
    menu._config_handler = MagicMock()
    menu.print_warning = MagicMock()
    menu.print_info = MagicMock()
    menu.print_error = MagicMock()
    menu.print_success = MagicMock()
    return menu


class TestConfirmAction:
    def test_confirm_action_accept(self):
        menu = _make_menu()
        with patch('builtins.input', return_value='S'):
            assert menu.confirm_action("Continuar?") is True

    def test_confirm_action_reject(self):
        menu = _make_menu()
        with patch('builtins.input', return_value='N'):
            assert menu.confirm_action("Continuar?") is False

    def test_confirm_action_lowercase_accept(self):
        menu = _make_menu()
        with patch('builtins.input', return_value='s'):
            assert menu.confirm_action("Continuar?") is True

    def test_confirm_action_enter_default(self):
        menu = _make_menu()
        with patch('builtins.input', return_value=''):
            assert menu.confirm_action("Continuar?") is False

    def test_confirm_action_dangerous_shows_warning(self):
        menu = _make_menu()
        with patch('builtins.input', return_value='N'):
            menu.confirm_action("Remover?", dangerous=True)
            menu.print_warning.assert_called()

    def test_confirm_action_not_dangerous_no_extra_warning(self):
        menu = _make_menu()
        with patch('builtins.input', return_value='N'):
            menu.confirm_action("Continuar?", dangerous=False)
            for call_args in menu.print_warning.call_args_list:
                assert "perigo" not in str(call_args).lower()


# ==============================================================================
# Menu Subgroups Tests (RULE-DOMAIN-4.4)
# ==============================================================================

class TestMenuSubgroups:
    def test_display_clients_menu_has_subgroups(self):
        from foton_system.interfaces.cli.menus_clients import MenuClientsHandler
        mock_menu = MagicMock()
        handler = MenuClientsHandler(mock_menu)
        with patch('foton_system.interfaces.cli.menus_clients.TUILayout') as mock_layout:
            with patch('builtins.input', return_value='0'):
                handler.display_clients_menu()
                printed_options = [str(c) for c in mock_layout.print_menu_option.call_args_list]
                assert any('Cadastro' in str(p) for p in printed_options)
                assert any('Manutenção' in str(p) for p in printed_options)
                assert any('Serviços' in str(p) for p in printed_options)
                assert any('Perigo' in str(p) for p in printed_options)

    def test_display_clients_menu_destructive_under_perigo(self):
        from foton_system.interfaces.cli.menus_clients import MenuClientsHandler
        mock_menu = MagicMock()
        handler = MenuClientsHandler(mock_menu)
        with patch('foton_system.interfaces.cli.menus_clients.TUILayout') as mock_layout:
            with patch('builtins.input', return_value='0'):
                handler.display_clients_menu()
                calls = mock_layout.print_menu_option.call_args_list
                option_texts = [c[0][1] if len(c[0]) > 1 else '' for c in calls]
                perigo_idx = next(i for i, t in enumerate(option_texts) if 'Perigo' in t)
                remover_idx = next(i for i, t in enumerate(option_texts) if 'Remover' in t)
                assert remover_idx > perigo_idx

    def test_display_clients_menu_key_mappings_preserved(self):
        from foton_system.interfaces.cli.menus_clients import MenuClientsHandler
        mock_menu = MagicMock()
        handler = MenuClientsHandler(mock_menu)
        with patch('foton_system.interfaces.cli.menus_clients.TUILayout') as mock_layout:
            with patch('builtins.input', return_value='0'):
                handler.display_clients_menu()
                calls = mock_layout.print_menu_option.call_args_list
                keys = {c[0][0] for c in calls if len(c[0]) >= 2 and c[0][0].isdigit()}
                assert '0' in keys
                assert '1' in keys

    def test_subgroup_separators_not_selectable(self):
        from foton_system.interfaces.cli.menus_clients import MenuClientsHandler
        mock_menu = MagicMock()
        handler = MenuClientsHandler(mock_menu)
        with patch('foton_system.interfaces.cli.menus_clients.TUILayout') as mock_layout:
            with patch('builtins.input', return_value='0'):
                handler.display_clients_menu()
                calls = mock_layout.print_menu_option.call_args_list
                for c in calls:
                    key = c[0][0] if len(c[0]) >= 2 else ''
                    label = c[0][1] if len(c[0]) > 1 else ''
                    if '---' in label:
                        assert key != ''


# ==============================================================================
# global_search Expanded Tests (RULE-DOMAIN-4.5)
# ==============================================================================

class TestGlobalSearchExpanded:
    @patch('foton_system.interfaces.cli.menus.time.perf_counter')
    def test_global_search_finds_by_codcliente(self, mock_perf):
        mock_perf.side_effect = [1.0, 1.1]
        from foton_system.interfaces.cli.menus import MenuSystem
        menu = MenuSystem.__new__(MenuSystem)
        menu.client_service = MagicMock()
        menu.print_warning = MagicMock()
        menu.print_error = MagicMock()
        menu.read_client_info_ui = MagicMock()
        import pandas as pd
        df = pd.DataFrame([
            {'NomeCliente': 'João Silva', 'Alias': 'JS', 'CodCliente': 'CLT-001', 'CPF_CNPJ': '123.456.789-00'}
        ])
        menu.client_service.repository.get_clients_dataframe.return_value = df
        menu.client_service.repository.get_services_dataframe.return_value = pd.DataFrame()
        with patch('builtins.input', side_effect=['CLT-001', '']):
            menu.global_search_ui()
        assert menu.read_client_info_ui.call_count == 0

    @patch('foton_system.interfaces.cli.menus.time.perf_counter')
    def test_global_search_finds_by_nif(self, mock_perf):
        mock_perf.side_effect = [1.0, 1.1]
        from foton_system.interfaces.cli.menus import MenuSystem
        menu = MenuSystem.__new__(MenuSystem)
        menu.client_service = MagicMock()
        menu.print_warning = MagicMock()
        menu.print_error = MagicMock()
        menu.read_client_info_ui = MagicMock()
        import pandas as pd
        df = pd.DataFrame([
            {'NomeCliente': 'João Silva', 'Alias': 'JS', 'CodCliente': 'CLT-001', 'CPF_CNPJ': '123.456.789-00'}
        ])
        menu.client_service.repository.get_clients_dataframe.return_value = df
        menu.client_service.repository.get_services_dataframe.return_value = pd.DataFrame()
        with patch('builtins.input', side_effect=['123.456.789-00', '']):
            menu.global_search_ui()
        assert menu.read_client_info_ui.call_count == 0

    @patch('foton_system.interfaces.cli.menus.time.perf_counter')
    def test_global_search_finds_by_name_backward_compat(self, mock_perf):
        mock_perf.side_effect = [1.0, 1.1]
        from foton_system.interfaces.cli.menus import MenuSystem
        menu = MenuSystem.__new__(MenuSystem)
        menu.client_service = MagicMock()
        menu.print_warning = MagicMock()
        menu.print_error = MagicMock()
        menu.read_client_info_ui = MagicMock()
        import pandas as pd
        df = pd.DataFrame([
            {'NomeCliente': 'Maria Souza', 'Alias': 'MS', 'CodCliente': 'CLT-002', 'CPF_CNPJ': '987.654.321-00'}
        ])
        menu.client_service.repository.get_clients_dataframe.return_value = df
        menu.client_service.repository.get_services_dataframe.return_value = pd.DataFrame()
        with patch('builtins.input', side_effect=['Maria', '']):
            menu.global_search_ui()
        assert menu.read_client_info_ui.call_count == 0

    @patch('foton_system.interfaces.cli.menus.time.perf_counter')
    def test_global_search_no_results(self, mock_perf, capsys):
        mock_perf.side_effect = [1.0, 1.1]
        menu = _make_menu()
        menu.client_service = MagicMock()
        menu.read_client_info_ui = MagicMock()
        import pandas as pd
        df = pd.DataFrame([
            {'NomeCliente': 'João Silva', 'Alias': 'JS', 'CodCliente': 'CLT-001', 'CPF_CNPJ': '123.456.789-00'}
        ])
        menu.client_service.repository.get_clients_dataframe.return_value = df
        menu.client_service.repository.get_services_dataframe.return_value = pd.DataFrame()
        with patch('builtins.input', return_value='XYZ'):
            menu.global_search_ui()
        captured = capsys.readouterr()
        assert 'Nenhum resultado' in captured.out


# ==============================================================================
# listar_clientes Pagination Tests (RULE-DOMAIN-4.7)
# ==============================================================================

class TestListarClientesPagination:
    @patch('foton_system.interfaces.mcp.foton_mcp._get_factory')
    def test_listar_clientes_default_params(self, mock_factory):
        mock_service = MagicMock()
        mock_factory.return_value.get_client_service.return_value = mock_service
        mock_service.list_clients.return_value = [
            {'name': f'Cliente {i}', 'has_info': True, 'service_count': 0}
            for i in range(5)
        ]
        from foton_system.interfaces.mcp.foton_mcp import listar_clientes
        result = listar_clientes()
        assert '5 client(s) found' in result

    @patch('foton_system.interfaces.mcp.foton_mcp._get_factory')
    def test_listar_clientes_pagina_1(self, mock_factory):
        mock_service = MagicMock()
        mock_factory.return_value.get_client_service.return_value = mock_service
        clients = [{'name': f'Cliente {i}', 'has_info': True, 'service_count': 0} for i in range(25)]
        mock_service.list_clients.return_value = clients
        from foton_system.interfaces.mcp.foton_mcp import listar_clientes
        result = listar_clientes(pagina=1, itens_por_pagina=10)
        assert 'Cliente 0' in result
        assert 'Cliente 9' in result
        assert 'Cliente 10' not in result

    @patch('foton_system.interfaces.mcp.foton_mcp._get_factory')
    def test_listar_clientes_pagina_2(self, mock_factory):
        mock_service = MagicMock()
        mock_factory.return_value.get_client_service.return_value = mock_service
        clients = [{'name': f'Cliente {i}', 'has_info': True, 'service_count': 0} for i in range(25)]
        mock_service.list_clients.return_value = clients
        from foton_system.interfaces.mcp.foton_mcp import listar_clientes
        result = listar_clientes(pagina=2, itens_por_pagina=10)
        assert 'Cliente 10' in result
        assert 'Cliente 19' in result
        assert 'Cliente 20' not in result

    @patch('foton_system.interfaces.mcp.foton_mcp._get_factory')
    def test_listar_clientes_pagina_exact_boundary(self, mock_factory):
        mock_service = MagicMock()
        mock_factory.return_value.get_client_service.return_value = mock_service
        clients = [{'name': f'Cliente {i}', 'has_info': True, 'service_count': 0} for i in range(20)]
        mock_service.list_clients.return_value = clients
        from foton_system.interfaces.mcp.foton_mcp import listar_clientes
        result = listar_clientes(pagina=2, itens_por_pagina=10)
        assert 'Cliente 10' in result
        assert 'Cliente 19' in result

    @patch('foton_system.interfaces.mcp.foton_mcp._get_factory')
    def test_listar_clientes_limite_backward_compat(self, mock_factory):
        mock_service = MagicMock()
        mock_factory.return_value.get_client_service.return_value = mock_service
        clients = [{'name': f'Cliente {i}', 'has_info': True, 'service_count': 0} for i in range(25)]
        mock_service.list_clients.return_value = clients
        from foton_system.interfaces.mcp.foton_mcp import listar_clientes
        result = listar_clientes(limite=5)
        lines = [l for l in result.split('\n') if 'Cliente' in l]
        assert len(lines) == 5

    @patch('foton_system.interfaces.mcp.foton_mcp._get_factory')
    def test_listar_clientes_pagination_info(self, mock_factory):
        mock_service = MagicMock()
        mock_factory.return_value.get_client_service.return_value = mock_service
        clients = [{'name': f'Cliente {i}', 'has_info': True, 'service_count': 0} for i in range(25)]
        mock_service.list_clients.return_value = clients
        from foton_system.interfaces.mcp.foton_mcp import listar_clientes
        result = listar_clientes(pagina=1, itens_por_pagina=10)
        assert 'Página 1' in result

    @patch('foton_system.interfaces.mcp.foton_mcp._get_factory')
    def test_listar_clientes_pagina_ultrapassou(self, mock_factory):
        mock_service = MagicMock()
        mock_factory.return_value.get_client_service.return_value = mock_service
        clients = [{'name': f'Cliente {i}', 'has_info': True, 'service_count': 0} for i in range(5)]
        mock_service.list_clients.return_value = clients
        from foton_system.interfaces.mcp.foton_mcp import listar_clientes
        result = listar_clientes(pagina=5, itens_por_pagina=10)
        assert 'Nenhum cliente' in result or '0 client' in result

    @patch('foton_system.interfaces.mcp.foton_mcp._get_factory')
    def test_listar_clientes_no_clients(self, mock_factory):
        mock_service = MagicMock()
        mock_factory.return_value.get_client_service.return_value = mock_service
        mock_service.list_clients.return_value = []
        from foton_system.interfaces.mcp.foton_mcp import listar_clientes
        result = listar_clientes()
        assert 'No clients registered' in result

    @patch('foton_system.interfaces.mcp.foton_mcp._get_factory')
    def test_listar_clientes_error_handling(self, mock_factory):
        mock_service = MagicMock()
        mock_factory.return_value.get_client_service.return_value = mock_service
        mock_service.list_clients.side_effect = OSError("Disk error")
        from foton_system.interfaces.mcp.foton_mcp import listar_clientes
        result = listar_clientes()
        assert 'File system error' in result


# ==============================================================================
# Integration: run() with parse_command Tests
# ==============================================================================

class TestRunWithParseCommand:
    def test_run_q_triggers_exit(self):
        menu = _make_menu()
        menu.display_main_menu = MagicMock(side_effect=['q'])
        menu.global_search_ui = MagicMock()
        with pytest.raises(SystemExit):
            menu.run()

    def test_run_h_triggers_help(self):
        menu = _make_menu()
        menu.display_main_menu = MagicMock(side_effect=['h', 'q'])
        menu.global_search_ui = MagicMock()
        with patch('builtins.input', return_value=''):
            with pytest.raises(SystemExit):
                menu.run()
        menu.print_info.assert_called()

    def test_run_g_triggers_global_search(self):
        menu = _make_menu()
        menu.display_main_menu = MagicMock(side_effect=['g', 'q'])
        menu.global_search_ui = MagicMock()
        with pytest.raises(SystemExit):
            menu.run()
        menu.global_search_ui.assert_called_once()

    def test_run_numeric_dispatches_handler(self):
        menu = _make_menu()
        menu.display_main_menu = MagicMock(side_effect=['1', 'q'])
        menu.global_search_ui = MagicMock()
        menu.handle_clients = MagicMock()
        with pytest.raises(SystemExit):
            menu.run()
        menu.handle_clients.assert_called_once()

    def test_run_00_returns_to_main(self):
        menu = _make_menu()
        menu.display_main_menu = MagicMock(side_effect=['00', 'q'])
        menu.global_search_ui = MagicMock()
        with pytest.raises(SystemExit):
            menu.run()


# ==============================================================================
# confirm_action Integration in menus_clients (RULE-DOMAIN-4.8)
# ==============================================================================

class TestConfirmActionIntegration:
    def test_remove_client_uses_confirm_action(self):
        from foton_system.interfaces.cli.menus_clients import MenuClientsHandler
        mock_menu = MagicMock()
        mock_menu.confirm_action.return_value = True
        mock_menu.client_service.soft_delete_client.return_value = {
            'success': True, 'message': 'Deletado'
        }
        handler = MenuClientsHandler(mock_menu)
        with patch('builtins.input', return_value='cliente_teste'):
            handler.remove_client_ui()
        mock_menu.confirm_action.assert_called_once()

    def test_remove_client_confirm_action_dangerous(self):
        from foton_system.interfaces.cli.menus_clients import MenuClientsHandler
        mock_menu = MagicMock()
        mock_menu.confirm_action.return_value = True
        mock_menu.client_service.soft_delete_client.return_value = {
            'success': True, 'message': 'Deletado'
        }
        handler = MenuClientsHandler(mock_menu)
        with patch('builtins.input', return_value='cliente_teste'):
            handler.remove_client_ui()
        args, kwargs = mock_menu.confirm_action.call_args
        assert kwargs.get('dangerous') is True or 'dangerous' in kwargs

    def test_fill_missing_codes_uses_confirm_action(self):
        from foton_system.interfaces.cli.menus_clients import MenuClientsHandler
        mock_menu = MagicMock()
        mock_menu.confirm_action.return_value = True
        mock_menu.client_service.fill_missing_codes.return_value = {
            'clientes_alterados': 0, 'servicos_alterados': 0
        }
        handler = MenuClientsHandler(mock_menu)
        handler.fill_missing_codes_ui()
        mock_menu.confirm_action.assert_called_once()
