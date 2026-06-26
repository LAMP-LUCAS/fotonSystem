import unittest
from unittest.mock import MagicMock, patch, call
from typing import Any, Callable
from foton_system.interfaces.cli.menus import MenuSystem
from foton_system.interfaces.cli.views.tui_layout import TUILayout

class TestMenuUI(unittest.TestCase):
    def setUp(self):
        # Patching dependencies to avoid real IDO/DB access
        patcher_repo = patch('foton_system.modules.clients.infrastructure.repositories.excel_client_repository.ExcelClientRepository')
        patcher_docx = patch('foton_system.modules.documents.infrastructure.adapters.python_docx_adapter.PythonDocxAdapter')
        patcher_pptx = patch('foton_system.modules.documents.infrastructure.adapters.python_pptx_adapter.PythonPPTXAdapter')
        mock_repo = patcher_repo.start()
        patcher_docx.start()
        patcher_pptx.start()
        self.menu = MenuSystem()
        self._repo_mock = mock_repo
        self._patchers = [patcher_repo, patcher_docx, patcher_pptx]

    def tearDown(self):
        for p in self._patchers:
            p.stop()

    # ----- helpers -----
    def _navigate_to(self, *inputs):
        """Helper: navega com side_effect de inputs e retorna o print capturado."""
        with patch('builtins.input', side_effect=list(inputs) + ['0']), \
             patch('builtins.print') as mock_print:
            with self.assertRaises(SystemExit):
                self.menu.run()
            return "".join([call.args[0] for call in mock_print.call_args_list if call.args])

    # ----- main menu -----
    def test_main_menu_display(self):
        """Valida se o menu principal contém as opções esperadas."""
        with patch('builtins.input', return_value='0'), \
             patch('builtins.print') as mock_print:
            with self.assertRaises(SystemExit):
                self.menu.run()
            
            # Verifica se as opções principais estão sendo impressas
            printed_content = "".join([call.args[0] for call in mock_print.call_args_list if call.args])
            self.assertIn("Gerenciar Clientes", printed_content)
            self.assertIn("Gerenciar Serviços", printed_content)
            self.assertIn("Documentos", printed_content)
            self.assertIn("Produtividade", printed_content)
            self.assertIn("Configurações", printed_content)
            self.assertIn("Sair", printed_content)

    # ----- main menu no-op cleanup (STORY-009 / RULE-UX-1.4) -----
    def test_main_menu_00_goes_home(self):
        """STORY-016: '00' retorna ao menu principal (home) sem erro."""
        with patch('builtins.input', side_effect=['00', '0']), \
             patch('builtins.print') as mock_print:
            with self.assertRaises(SystemExit):
                self.menu.run()
            printed_content = "".join([call.args[0] for call in mock_print.call_args_list if call.args])
            self.assertNotIn("Opção inválida", printed_content)

    # ----- breadcrumb tests (STORY-003 / RULE-UX-1.1) -----
    def test_clients_menu_shows_breadcrumb(self):
        """RULE-UX-1.1: display_clients_menu exibe breadcrumb 'Clientes'."""
        with patch.object(self.menu, 'print_breadcrumb') as mock_bc:
            self._navigate_to('1', '0')
            mock_bc.assert_any_call(["Clientes"])

    def test_services_menu_shows_breadcrumb(self):
        """RULE-UX-1.1: display_services_menu exibe breadcrumb 'Serviços'."""
        with patch.object(self.menu, 'print_breadcrumb') as mock_bc:
            self._navigate_to('2', '0')
            mock_bc.assert_any_call(["Serviços"])

    def test_documents_menu_shows_breadcrumb(self):
        """RULE-UX-1.1: display_documents_menu exibe breadcrumb 'Documentos'."""
        with patch.object(self.menu, 'print_breadcrumb') as mock_bc:
            self._navigate_to('4', '0')
            mock_bc.assert_any_call(["Documentos"])

    def test_finance_menu_shows_breadcrumb(self):
        """RULE-UX-1.1: display_finance_menu exibe breadcrumb 'Financeiro'."""
        with patch.object(self.menu, 'print_breadcrumb') as mock_bc:
            self._navigate_to('5', '0')
            mock_bc.assert_any_call(["Financeiro"])

    def test_productivity_menu_shows_breadcrumb(self):
        """RULE-UX-1.1: display_productivity_menu exibe breadcrumb 'Produtividade'."""
        with patch.object(self.menu, 'print_breadcrumb') as mock_bc:
            self._navigate_to('6', '0')
            mock_bc.assert_any_call(["Produtividade"])

    def test_settings_menu_shows_breadcrumb(self):
        """RULE-UX-1.1: display_settings_menu exibe breadcrumb 'Configurações'."""
        with patch.object(self.menu, 'print_breadcrumb') as mock_bc:
            self._navigate_to('7', '0')
            mock_bc.assert_any_call(["Configurações"])

    # ----- menu label tests (STORY-002 / RULE-UX-4.2) -----
    def test_clients_menu_shows_remover_cliente(self):
        """RULE-UX-4.2: Opção 9 exibe 'Remover Cliente' sem '(Soft Delete)'."""
        with patch('builtins.input', side_effect=['1', '0', '0']), \
             patch('builtins.print') as mock_print:
            with self.assertRaises(SystemExit):
                self.menu.run()
            content = "".join([c.args[0] for c in mock_print.call_args_list if c.args])
            self.assertIn("Remover Cliente", content)
            self.assertNotIn("Soft Delete", content)

    # ----- back shortcut 'b' tests (STORY-008 / RULE-UX-1.2) -----
    def test_clients_back_with_b(self):
        """RULE-UX-1.2: 'b' no menu clientes volta ao menu principal."""
        with patch('builtins.input', side_effect=['1', 'b', '0']), \
             patch('builtins.print'):
            with self.assertRaises(SystemExit):
                self.menu.run()

    def test_clients_back_with_B_uppercase(self):
        """RULE-UX-1.2: 'B' maiúsculo também volta."""
        with patch('builtins.input', side_effect=['1', 'B', '0']), \
             patch('builtins.print'):
            with self.assertRaises(SystemExit):
                self.menu.run()

    def test_clients_back_with_zero_still_works(self):
        """RULE-UX-1.2: '0' continua funcionando (backward compat)."""
        with patch('builtins.input', side_effect=['1', '0', '0']), \
             patch('builtins.print'):
            with self.assertRaises(SystemExit):
                self.menu.run()

    def test_services_back_with_b(self):
        """RULE-UX-1.2: 'b' no menu serviços volta ao menu principal."""
        with patch('builtins.input', side_effect=['2', 'b', '0']), \
             patch('builtins.print'):
            with self.assertRaises(SystemExit):
                self.menu.run()

    def test_documents_back_with_b(self):
        """RULE-UX-1.2: 'b' no menu documentos volta ao menu principal."""
        with patch('builtins.input', side_effect=['4', 'b', '0']), \
             patch('builtins.print'):
            with self.assertRaises(SystemExit):
                self.menu.run()

    def test_finance_back_with_b(self):
        """RULE-UX-1.2: 'b' no menu financeiro volta ao menu principal."""
        with patch('builtins.input', side_effect=['5', 'b', '0']), \
             patch('builtins.print'):
            with self.assertRaises(SystemExit):
                self.menu.run()

    def test_productivity_back_with_b(self):
        """RULE-UX-1.2: 'b' no menu produtividade volta ao menu principal."""
        with patch('builtins.input', side_effect=['6', 'b', '0']), \
             patch('builtins.print'):
            with self.assertRaises(SystemExit):
                self.menu.run()

    def test_settings_back_with_b(self):
        """RULE-UX-1.2: 'b' no menu configurações volta ao menu principal."""
        with patch('builtins.input', side_effect=['7', 'b', '0']), \
             patch('builtins.print'):
            with self.assertRaises(SystemExit):
                self.menu.run()

    def test_client_servicos_back_with_b(self):
        """RULE-UX-1.2: 'b' no submenu serviços do cliente volta ao menu clientes."""
        with patch('builtins.input', side_effect=['1', '10', 'b', 'x', '0', '0']), \
             patch('builtins.print'):
            with self.assertRaises(SystemExit):
                self.menu.run()

    def test_client_sync_menu_back_with_b(self):
        """RULE-UX-1.2: 'b' no submenu sincronizar cadastro volta."""
        with patch('builtins.input', side_effect=['1', '11', 'b', '0', '0']), \
             patch('builtins.print'):
            with self.assertRaises(SystemExit):
                self.menu.run()

    def test_service_sync_menu_back_with_b(self):
        """RULE-UX-1.2: 'b' no submenu sincronizar serviços volta."""
        with patch('builtins.input', side_effect=['2', '4', 'b', '0', '0']), \
             patch('builtins.print'):
            with self.assertRaises(SystemExit):
                self.menu.run()

    # ----- search drill-down tests (STORY-004 / RULE-UX-3.x) -----
    def test_search_client_ui_empty_term_lists_all(self):
        """RULE-UX-3.4: Termo vazio chama list_all_clients_ui."""
        with patch('builtins.input', return_value=''), \
             patch('builtins.print'):
            with patch.object(self.menu, 'list_all_clients_ui') as mock_list:
                self.menu.search_client_ui()
        mock_list.assert_called_once()

    def test_search_client_ui_numbers_results(self):
        """RULE-UX-3.1: Resultados numerados 1..N com prompt de seleção."""
        import pandas as pd
        from unittest.mock import MagicMock
        repo_mock = MagicMock()
        df = pd.DataFrame({
            'NomeCliente': ['Ana Silva', 'Carlos Souza'],
            'Alias': ['ana', 'carlos'],
        })
        repo_mock.get_clients_dataframe.return_value = df
        self.menu.client_repo = repo_mock
        self.menu.client_service.repository = repo_mock
        with patch('builtins.input', side_effect=['silva', '']), \
             patch('builtins.print') as mock_print:
            self.menu.search_client_ui()
        printed = "".join([c.args[0] for c in mock_print.call_args_list if c.args])
        self.assertIn("1.", printed)
        self.assertIn("Ana Silva", printed)
        self.assertIn("Resultados para", printed)
        self.assertIn("Cliente: ana", printed)

    def test_search_client_ui_select_navigates_to_read(self):
        """RULE-UX-3.1+3.3: Selecionar número abre read_client_info_ui."""
        import pandas as pd
        from unittest.mock import MagicMock
        repo_mock = MagicMock()
        df = pd.DataFrame({
            'NomeCliente': ['Ana Silva', 'Carlos Souza'],
            'Alias': ['ana', 'carlos'],
        })
        repo_mock.get_clients_dataframe.return_value = df
        self.menu.client_repo = repo_mock
        self.menu.client_service.repository = repo_mock
        with patch('builtins.input', side_effect=['silva', '1']), \
             patch('builtins.print'):
            with patch.object(self.menu, 'read_client_info_ui') as mock_read:
                self.menu.search_client_ui()
        mock_read.assert_called_once()

    def test_search_client_ui_enter_returns_without_read(self):
        """RULE-UX-3.1: ENTER sem seleção volta sem abrir ficha."""
        import pandas as pd
        from unittest.mock import MagicMock
        repo_mock = MagicMock()
        df = pd.DataFrame({
            'NomeCliente': ['Ana Silva'],
            'Alias': ['ana'],
        })
        repo_mock.get_clients_dataframe.return_value = df
        self.menu.client_repo = repo_mock
        self.menu.client_service.repository = repo_mock
        with patch('builtins.input', side_effect=['silva', '']), \
             patch('builtins.print'):
            with patch.object(self.menu, 'read_client_info_ui') as mock_read:
                self.menu.search_client_ui()
        mock_read.assert_not_called()

    def test_global_search_ui_numbers_client_results(self):
        """RULE-UX-3.2: Clientes numerados na busca global."""
        import pandas as pd
        from unittest.mock import MagicMock
        repo_mock = MagicMock()
        df_clients = pd.DataFrame({
            'NomeCliente': ['Ana Silva'],
            'Alias': ['ana'],
        })
        df_services = pd.DataFrame({
            'AliasCliente': pd.Series(dtype='object'),
            'Alias': pd.Series(dtype='object'),
        })
        repo_mock.get_clients_dataframe.return_value = df_clients
        repo_mock.get_services_dataframe.return_value = df_services
        self.menu.client_repo = repo_mock
        self.menu.client_service.repository = repo_mock
        with patch('builtins.print') as mock_print:
            with patch('builtins.input', side_effect=['silva', '']):
                self.menu.global_search_ui()
        printed = "".join([c.args[0] for c in mock_print.call_args_list if c.args])
        self.assertIn("1.", printed)
        self.assertIn("Ana Silva", printed)

    def test_global_search_ui_select_navigates_to_read(self):
        """RULE-UX-3.2+3.3: Selecionar cliente na busca global abre ficha."""
        import pandas as pd
        from unittest.mock import MagicMock
        repo_mock = MagicMock()
        df_clients = pd.DataFrame({
            'NomeCliente': ['Ana Silva'],
            'Alias': ['ana'],
        })
        df_services = pd.DataFrame({
            'AliasCliente': pd.Series(dtype='object'),
            'Alias': pd.Series(dtype='object'),
        })
        repo_mock.get_clients_dataframe.return_value = df_clients
        repo_mock.get_services_dataframe.return_value = df_services
        self.menu.client_repo = repo_mock
        self.menu.client_service.repository = repo_mock
        with patch('builtins.input', side_effect=['silva', '1']), \
             patch('builtins.print'):
            with patch.object(self.menu, 'read_client_info_ui') as mock_read:
                self.menu.global_search_ui()
        mock_read.assert_called_once()

    # ----- list all clients marker tests (STORY-001 / RULE-UX-2.4) -----
    def test_list_all_clients_shows_deleted_marker(self):
        """RULE-UX-2.4: Cliente DELETADO aparece com [DELETADO] na listagem."""
        import pandas as pd
        from unittest.mock import MagicMock
        repo_mock = MagicMock()
        df = pd.DataFrame({
            'CodCliente': ['C001'],
            'NomeCliente': ['Cliente Removido'],
            'Alias': ['removido'],
            'Status': ['DELETADO'],
        })
        repo_mock.get_all_clients_dataframe.return_value = df
        self.menu.client_repo = repo_mock
        with patch('builtins.input', side_effect=['', '']), \
             patch('builtins.print') as mock_print:
            self.menu.list_all_clients_ui()
        printed = "".join([c.args[0] for c in mock_print.call_args_list if c.args])
        self.assertIn("[DELETADO]", printed)


# ----- pagination tests (STORY-005 / RULE-UX-2.2, RULE-UX-2.3) -----

class TestPagination(unittest.TestCase):
    """Testes para o helper paginate_items."""

    def test_paginate_items_empty(self):
        """Lista vazia exibe mensagem amigável."""
        items = []
        with patch('builtins.print') as mock_print:
            TUILayout.paginate_items(items, render_item=lambda x, i: None, empty_msg="Nada aqui.")
        printed = "".join(c.args[0] for c in mock_print.call_args_list if c.args)
        self.assertIn("Nada aqui.", printed)

    def test_paginate_items_single_page(self):
        """Menos de 10 itens mostra tudo em uma página."""
        items = list(range(5))
        rendered = []
        with patch('builtins.input', return_value=''):
            TUILayout.paginate_items(items, render_item=lambda x, i: rendered.append((x, i)))
        self.assertEqual(len(rendered), 5)
        self.assertEqual(rendered[0], (0, 1))
        self.assertEqual(rendered[4], (4, 5))

    def test_paginate_items_multi_page(self):
        """25 itens → 3 páginas, render_item chamado para todos."""
        items = list(range(25))
        rendered = []
        with patch('builtins.input', side_effect=['', '']):
            TUILayout.paginate_items(items, render_item=lambda x, i: rendered.append((x, i)))
        self.assertEqual(len(rendered), 25)

    def test_paginate_items_page_indicator(self):
        """Indicador 'Página X de Y' aparece nos cabeçalhos."""
        items = list(range(25))
        with patch('builtins.input', side_effect=['', '']), \
             patch('builtins.print') as mock_print:
            TUILayout.paginate_items(items, render_item=lambda x, i: None)
        printed = "".join(c.args[0] for c in mock_print.call_args_list if c.args)
        self.assertIn("Página 1 de 3", printed)
        self.assertIn("Página 2 de 3", printed)
        self.assertIn("Página 3 de 3", printed)

    def test_paginate_items_exact_page_size(self):
        """Exatamente 10 itens exibe tudo em uma página."""
        items = list(range(10))
        rendered = []
        with patch('builtins.input', return_value=''):
            TUILayout.paginate_items(items, render_item=lambda x, i: rendered.append((x, i)))
        self.assertEqual(len(rendered), 10)

    def test_paginate_items_returns_count(self):
        """Retorna o número total de itens (0 se vazio)."""
        self.assertEqual(TUILayout.paginate_items([], render_item=lambda x, i: None), 0)
        self.assertEqual(TUILayout.paginate_items([1, 2, 3], render_item=lambda x, i: None), 3)
        with patch('builtins.input', return_value=''):
            result = TUILayout.paginate_items(list(range(25)), render_item=lambda x, i: None)
        self.assertEqual(result, 25)

    def test_paginate_items_correct_index_per_page(self):
        """Índices reiniciam em cada página? Não — devem ser contínuos."""
        items = list(range(15))
        indices = []
        with patch('builtins.input', side_effect=['']):
            TUILayout.paginate_items(items, render_item=lambda x, i: indices.append(i))
        self.assertEqual(indices, list(range(1, 16)))


# ----- performance baseline tests (PRD EPIC-001 metrics) -----

class TestMenuPerformance(unittest.TestCase):
    """Testes de baseline de performance para operações de navegação."""

    def setUp(self):
        import pandas as pd
        from unittest.mock import MagicMock
        from foton_system.interfaces.cli.menus import MenuSystem
        self.menu = MenuSystem()
        repo_mock = MagicMock()
        big_df = pd.DataFrame({
            'CodCliente': [f'C{i:03d}' for i in range(100)],
            'NomeCliente': [f'Cliente {i}' for i in range(100)],
            'Alias': [f'cli{i}' for i in range(100)],
            'Status': ['ATIVO'] * 100,
        })
        empty_services = pd.DataFrame({
            'AliasCliente': pd.Series(dtype='object'),
            'Alias': pd.Series(dtype='object'),
        })
        repo_mock.get_all_clients_dataframe.return_value = big_df
        repo_mock.get_clients_dataframe.return_value = big_df
        repo_mock.get_services_dataframe.return_value = empty_services
        self.menu.client_repo = repo_mock
        self.menu.client_service.repository = repo_mock

    def test_list_all_clients_performance_baseline(self):
        """list_all_clients_ui com 100 clientes deve completar em < 1s."""
        import time
        _dummy = [''] * 20
        with patch('builtins.input', side_effect=_dummy), \
             patch('builtins.print'):
            _start = time.perf_counter()
            self.menu.list_all_clients_ui()
            elapsed = time.perf_counter() - _start
        self.assertLess(elapsed, 1.0, f"list_all_clients_ui levou {elapsed:.3f}s")

    def test_search_client_performance_baseline(self):
        """search_client_ui com 100 clientes deve completar em < 1s."""
        import time
        with patch('builtins.input', side_effect=['cliente', '']), \
             patch('builtins.print'):
            _start = time.perf_counter()
            self.menu.search_client_ui()
            elapsed = time.perf_counter() - _start
        self.assertLess(elapsed, 1.0, f"search_client_ui levou {elapsed:.3f}s")

    def test_global_search_performance_baseline(self):
        """global_search_ui com 100 clientes deve completar em < 1s."""
        import time
        with patch('builtins.input', side_effect=['cliente', '']), \
             patch('builtins.print'):
            _start = time.perf_counter()
            self.menu.global_search_ui()
            elapsed = time.perf_counter() - _start
        self.assertLess(elapsed, 1.0, f"global_search_ui levou {elapsed:.3f}s")


if __name__ == '__main__':
    unittest.main()
