"""
Tests for STORY-015: UX Split menus.py + Helpers TUI.

Covers RULE-DOMAIN-4.1, RULE-DOMAIN-4.2, RULE-DOMAIN-4.3.
"""

import pytest
import time
import io
import sys
from unittest.mock import MagicMock, patch

# @story: STORY-015
# @rule: RULE-DOMAIN-4.1, RULE-DOMAIN-4.2, RULE-DOMAIN-4.3

# ==============================================================================
# ProgressTracker Tests (RULE-DOMAIN-4.2)
# ==============================================================================

class TestProgressTracker:
    def test_initialization(self):
        from foton_system.interfaces.cli.helpers.progress_tracker import ProgressTracker
        pt = ProgressTracker(total=10, description="Processando")
        assert pt.total == 10
        assert pt.description == "Processando"
        assert pt.current == 0

    def test_advance_increments_counter(self, capsys):
        from foton_system.interfaces.cli.helpers.progress_tracker import ProgressTracker
        pt = ProgressTracker(total=10, description="Sincronizando")
        pt.advance("CLIENTE_A")
        captured = capsys.readouterr()
        assert "[1/10]" in captured.out
        assert "Sincronizando" in captured.out
        assert pt.current == 1

    def test_advance_multiple_items(self, capsys):
        from foton_system.interfaces.cli.helpers.progress_tracker import ProgressTracker
        pt = ProgressTracker(total=3)
        pt.advance("A")
        pt.advance("B")
        pt.advance("C")
        assert pt.current == 3

    def test_advance_beyond_total_clamps(self, capsys):
        from foton_system.interfaces.cli.helpers.progress_tracker import ProgressTracker
        pt = ProgressTracker(total=2)
        pt.advance("X")
        pt.advance("Y")
        pt.advance("Z")
        assert pt.current == 2
        captured = capsys.readouterr()
        assert "[2/2]" in captured.out

    def test_finish_shows_elapsed(self, capsys):
        from foton_system.interfaces.cli.helpers.progress_tracker import ProgressTracker
        pt = ProgressTracker(total=5, description="Teste")
        pt.advance("A")
        pt.finish()
        captured = capsys.readouterr()
        assert "[5/5]" in captured.out
        assert "concluido" in captured.out

# ==============================================================================
# Error Suggestions Tests (RULE-DOMAIN-4.3)
# ==============================================================================

class TestErrorSuggestions:
    def test_file_not_found_error(self):
        from foton_system.interfaces.cli.helpers.error_suggestions import get_error_suggestion
        error = FileNotFoundError("Arquivo nao encontrado")
        suggestion = get_error_suggestion(error)
        assert "settings.json" in suggestion.lower()
        assert "arquivo" in suggestion.lower()

    def test_permission_error(self):
        from foton_system.interfaces.cli.helpers.error_suggestions import get_error_suggestion
        error = PermissionError("Acesso negado")
        suggestion = get_error_suggestion(error)
        assert "excel" in suggestion.lower()
        assert "feche" in suggestion.lower()

    def test_database_locked_error(self):
        from foton_system.interfaces.cli.helpers.error_suggestions import get_error_suggestion
        import sqlite3
        error = sqlite3.OperationalError("database is locked")
        suggestion = get_error_suggestion(error)
        assert "aberta" in suggestion.lower()
        assert "programa" in suggestion.lower()

    def test_unknown_error_fallback(self):
        from foton_system.interfaces.cli.helpers.error_suggestions import get_error_suggestion
        error = RuntimeError("Algo deu errado")
        suggestion = get_error_suggestion(error)
        assert "inesperado" in suggestion.lower()

    def test_format_error_with_suggestion(self):
        from foton_system.interfaces.cli.helpers.error_suggestions import format_error_with_suggestion
        error = FileNotFoundError("arquivo.txt nao encontrado")
        formatted = format_error_with_suggestion(error)
        assert "arquivo.txt" in formatted
        assert "Sugestao" in formatted
        assert "settings.json" in formatted.lower()

# ==============================================================================
# Menu Split Tests (RULE-DOMAIN-4.1)
# ==============================================================================

class TestMenuSplit:
    def test_menus_py_dispatch_maintains_entry_point(self):
        from foton_system.interfaces.cli.menus import MenuSystem
        with patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
             patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
             patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'):
            menu = MenuSystem()
        assert hasattr(menu, 'run')
        assert hasattr(menu, 'display_main_menu')
        assert hasattr(menu, 'print_success')
        assert hasattr(menu, '_ensure_database_exists')

    def test_menu_system_creates_handlers(self):
        from foton_system.interfaces.cli.menus import MenuSystem
        with patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
             patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
             patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'):
            menu = MenuSystem()
        assert hasattr(menu, '_clients_handler')
        assert hasattr(menu, '_finance_handler')
        assert hasattr(menu, '_docs_handler')
        assert hasattr(menu, '_config_handler')

    def test_getattr_delegates_to_clients_handler(self):
        from foton_system.interfaces.cli.menus import MenuSystem
        from foton_system.interfaces.cli.menus_clients import MenuClientsHandler
        with patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
             patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
             patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'):
            menu = MenuSystem()
        assert isinstance(menu._clients_handler, MenuClientsHandler)
        assert menu.handle_clients == menu._clients_handler.handle_clients
        assert menu.search_client_ui == menu._clients_handler.search_client_ui

    def test_getattr_delegates_to_finance_handler(self):
        from foton_system.interfaces.cli.menus import MenuSystem
        from foton_system.interfaces.cli.menus_finance import MenuFinanceHandler
        with patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
             patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
             patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'):
            menu = MenuSystem()
        assert isinstance(menu._finance_handler, MenuFinanceHandler)
        assert menu.handle_finance == menu._finance_handler.handle_finance
        assert menu.registrar_financeiro_ui == menu._finance_handler.registrar_financeiro_ui

    def test_getattr_delegates_to_docs_handler(self):
        from foton_system.interfaces.cli.menus import MenuSystem
        from foton_system.interfaces.cli.menus_docs import MenuDocsHandler
        with patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
             patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
             patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'):
            menu = MenuSystem()
        assert isinstance(menu._docs_handler, MenuDocsHandler)
        assert menu.handle_documents == menu._docs_handler.handle_documents
        assert menu.generate_document_ui == menu._docs_handler.generate_document_ui

    def test_getattr_delegates_to_config_handler(self):
        from foton_system.interfaces.cli.menus import MenuSystem
        from foton_system.interfaces.cli.menus_config import MenuConfigHandler
        with patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
             patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
             patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'):
            menu = MenuSystem()
        assert isinstance(menu._config_handler, MenuConfigHandler)
        assert menu.handle_settings == menu._config_handler.handle_settings
        assert menu.handle_watcher == menu._config_handler.handle_watcher

    def test_submodules_importable(self):
        from foton_system.interfaces.cli import menus_clients
        from foton_system.interfaces.cli import menus_finance
        from foton_system.interfaces.cli import menus_docs
        from foton_system.interfaces.cli import menus_config
        assert hasattr(menus_clients, 'MenuClientsHandler')
        assert hasattr(menus_finance, 'MenuFinanceHandler')
        assert hasattr(menus_docs, 'MenuDocsHandler')
        assert hasattr(menus_config, 'MenuConfigHandler')

    def test_helpers_module_importable(self):
        from foton_system.interfaces.cli.helpers import ProgressTracker
        from foton_system.interfaces.cli.helpers import get_error_suggestion
        from foton_system.interfaces.cli.helpers import format_error_with_suggestion
        assert ProgressTracker is not None
        assert callable(get_error_suggestion)
        assert callable(format_error_with_suggestion)

# ==============================================================================
# Backward Compatibility Tests (RULE-DOMAIN-4.1)
# ==============================================================================

class TestBackwardCompatibility:
    def test_clients_menu_import_via_menus_module(self):
        from foton_system.interfaces.cli.menus import MenuSystem
        from foton_system.interfaces.cli.menus_clients import MenuClientsHandler
        with patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
             patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
             patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'):
            menu = MenuSystem()
        assert callable(menu.handle_clients)
        assert callable(menu.create_client_ui)
        assert callable(menu.read_client_info_ui)

    def test_finance_menu_import_via_menus_module(self):
        from foton_system.interfaces.cli.menus import MenuSystem
        with patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
             patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
             patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'):
            menu = MenuSystem()
        assert callable(menu.handle_finance)
        assert callable(menu.registrar_financeiro_ui)
        assert callable(menu.consultar_financeiro_ui)
        assert callable(menu.resumo_financeiro_ui)

    def test_docs_menu_import_via_menus_module(self):
        from foton_system.interfaces.cli.menus import MenuSystem
        with patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
             patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
             patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'):
            menu = MenuSystem()
        assert callable(menu.handle_documents)
        assert callable(menu.generate_document_ui)
        assert callable(menu.validate_template_ui)

    def test_config_menu_import_via_menus_module(self):
        from foton_system.interfaces.cli.menus import MenuSystem
        with patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
             patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
             patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'):
            menu = MenuSystem()
        assert callable(menu.handle_settings)
        assert callable(menu.handle_installation)
        assert callable(menu.handle_watcher)
        assert callable(menu.start_pomodoro_ui)

    def test_services_menu_accessible(self):
        from foton_system.interfaces.cli.menus import MenuSystem
        with patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
             patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
             patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'):
            menu = MenuSystem()
        assert callable(menu.handle_services)
        assert callable(menu.handle_client_servicos_menu)
        assert callable(menu.create_client_servico_ui)

    def test_SystemProfile_still_importable(self):
        from foton_system.interfaces.cli.menus import SystemProfile
        assert SystemProfile is not None

    def test_print_helpers_stay_on_menusystem(self):
        from foton_system.interfaces.cli.menus import MenuSystem
        with patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
             patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
             patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'):
            menu = MenuSystem()
        assert callable(menu.print_success)
        assert callable(menu.print_error)
        assert callable(menu.print_warning)
        assert callable(menu.print_info)
        assert callable(menu.print_breadcrumb)
        assert callable(menu.print_header)

    def test_global_search_ui_stays_on_menusystem(self):
        from foton_system.interfaces.cli.menus import MenuSystem
        with patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
             patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
             patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'):
            menu = MenuSystem()
        assert callable(menu.global_search_ui)

    def test_select_from_list_stays_on_menusystem(self):
        from foton_system.interfaces.cli.menus import MenuSystem
        with patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
             patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
             patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'):
            menu = MenuSystem()
        assert callable(menu._select_from_list)

    def test_create_new_data_file_ui_stays_on_menusystem(self):
        from foton_system.interfaces.cli.menus import MenuSystem
        with patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
             patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
             patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'):
            menu = MenuSystem()
        assert callable(menu._create_new_data_file_ui)
