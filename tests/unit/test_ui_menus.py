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


# ----- NPS (RULE-UX-9.1, RULE-UX-9.2, RULE-TELEMETRY-1.5) -----
class TestNps(unittest.TestCase):
    """@story: STORY-021 @rule: RULE-UX-9.1, RULE-UX-9.2, RULE-TELEMETRY-1.5"""

    def setUp(self):
        patcher_repo = patch('foton_system.modules.clients.infrastructure.repositories.excel_client_repository.ExcelClientRepository')
        patcher_docx = patch('foton_system.modules.documents.infrastructure.adapters.python_docx_adapter.PythonDocxAdapter')
        patcher_pptx = patch('foton_system.modules.documents.infrastructure.adapters.python_pptx_adapter.PythonPPTXAdapter')
        patcher_repo.start()
        patcher_docx.start()
        patcher_pptx.start()
        from foton_system.interfaces.cli.menus import MenuSystem
        self.menu = MenuSystem()

    def tearDown(self):
        import unittest.mock as mock
        mock.patch.stopall()

    def test_nps_option_displayed(self):
        """Settings menu must show NPS option."""
        with patch('builtins.input', side_effect=['7', '0', '0']), \
             patch('builtins.print') as mock_print, \
             patch('foton_system.interfaces.cli.views.tui_layout.TUILayout.clear'):
            with self.assertRaises(SystemExit):
                self.menu.run()
            printed = "".join([call.args[0] for call in mock_print.call_args_list if call.args])
        self.assertIn("Pesquisa de Satisfação", printed)

    def test_nps_validates_range(self):
        """NPS must reject values outside 0-10."""
        from foton_system.interfaces.cli.menus_config import MenuConfigHandler
        handler = MenuConfigHandler(self.menu)
        with patch('builtins.input', side_effect=['999', '']), \
             patch('builtins.print') as mp:
            handler._pesquisa_nps_ui()
            printed = "".join(c.args[0] for c in mp.call_args_list if c.args)
        self.assertIn("inválida", printed.lower())

    def test_nps_stores_response_with_all_fields(self):
        """Valid NPS score saved with score, classification, comment, session context."""
        from foton_system.interfaces.cli.menus_config import MenuConfigHandler
        import tempfile, pathlib, json
        tmp = pathlib.Path(tempfile.mkdtemp())
        # Pre-create session.json with known counters
        session_data = {
            "total_sessoes_all_time": 42,
            "total_operacoes_all_time": 315,
            "session_id": "abc-123",
            "interface": "TUI"
        }
        (tmp / "session.json").write_text(json.dumps(session_data), encoding="utf-8")
        with patch('builtins.input', side_effect=['9', 'Excelente ferramenta!', '', '', '']), \
             patch('builtins.print'), \
             patch('foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service.BootstrapService.get_user_config_dir', return_value=tmp):
            handler = MenuConfigHandler(self.menu)
            handler._pesquisa_nps_ui()
        nps_file = tmp / "nps_responses.jsonl"
        self.assertTrue(nps_file.exists())
        content = nps_file.read_text(encoding='utf-8')
        record = json.loads(content.strip())
        self.assertEqual(record["score"], 9)
        self.assertEqual(record["classification"], "Promotor")
        self.assertEqual(record["comentario"], "Excelente ferramenta!")
        self.assertIn("session_count", record)
        self.assertIn("operation_count", record)
        self.assertIn("session_id", record)
        self.assertIn("interface", record)
        self.assertEqual(record["session_count"], 42)

    def test_nps_comment_skipped_when_empty(self):
        """Comment field is empty string when skipped."""
        from foton_system.interfaces.cli.menus_config import MenuConfigHandler
        import tempfile, pathlib, json
        tmp = pathlib.Path(tempfile.mkdtemp())
        session_data = {"total_sessoes_all_time": 1, "total_operacoes_all_time": 0, "session_id": "x", "interface": "TUI"}
        (tmp / "session.json").write_text(json.dumps(session_data), encoding="utf-8")
        with patch('builtins.input', side_effect=['9', '', '', '']), \
             patch('builtins.print'), \
             patch('foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service.BootstrapService.get_user_config_dir', return_value=tmp):
            handler = MenuConfigHandler(self.menu)
            handler._pesquisa_nps_ui()
        nps_file = tmp / "nps_responses.jsonl"
        record = json.loads(nps_file.read_text(encoding='utf-8').strip())
        self.assertEqual(record["comentario"], "")

    def test_nps_classification_not_displayed_to_user(self):
        """Classification must NOT appear in user-facing output."""
        from foton_system.interfaces.cli.menus_config import MenuConfigHandler
        import tempfile, pathlib, json
        tmp = pathlib.Path(tempfile.mkdtemp())
        session_data = {"total_sessoes_all_time": 1, "total_operacoes_all_time": 0, "session_id": "x", "interface": "TUI"}
        (tmp / "session.json").write_text(json.dumps(session_data), encoding="utf-8")
        with patch('builtins.input', side_effect=['9', '', '', '']), \
             patch('builtins.print') as mp, \
             patch('foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service.BootstrapService.get_user_config_dir', return_value=tmp):
            handler = MenuConfigHandler(self.menu)
            handler._pesquisa_nps_ui()
        printed = "".join(c.args[0] for c in mp.call_args_list if c.args)
        self.assertNotIn("Promotor", printed)
        self.assertNotIn("Detrator", printed)
        self.assertNotIn("Neutro", printed)

    def test_nps_trend_displayed(self):
        """Trend visual must appear after response."""
        from foton_system.interfaces.cli.menus_config import MenuConfigHandler
        import tempfile, pathlib, json
        tmp = pathlib.Path(tempfile.mkdtemp())
        # Pre-populate with 3 previous responses
        nps_file = tmp / "nps_responses.jsonl"
        for s in [5, 7, 9]:
            with open(nps_file, "a", encoding="utf-8") as f:
                f.write(json.dumps({"score": s, "timestamp": "2026-01-01T00:00:00", "classification": "x",
                                    "comentario": "", "session_count": 1, "operation_count": 0,
                                    "session_id": "x", "interface": "TUI"}) + "\n")
        session_data = {"total_sessoes_all_time": 1, "total_operacoes_all_time": 0, "session_id": "x", "interface": "TUI"}
        (tmp / "session.json").write_text(json.dumps(session_data), encoding="utf-8")
        with patch('builtins.input', side_effect=['10', '', '', '']), \
             patch('builtins.print') as mp, \
             patch('foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service.BootstrapService.get_user_config_dir', return_value=tmp):
            handler = MenuConfigHandler(self.menu)
            handler._pesquisa_nps_ui()
        printed = "".join(c.args[0] for c in mp.call_args_list if c.args)
        self.assertTrue("[+]" in printed or "[-]" in printed or "[=]" in printed)

    def test_nps_history_table_displayed(self):
        """Last 5 responses table must appear."""
        from foton_system.interfaces.cli.menus_config import MenuConfigHandler
        import tempfile, pathlib, json
        tmp = pathlib.Path(tempfile.mkdtemp())
        nps_file = tmp / "nps_responses.jsonl"
        for s in range(1, 7):
            with open(nps_file, "a", encoding="utf-8") as f:
                f.write(json.dumps({"score": s, "timestamp": f"2026-01-0{s}T00:00:00", "classification": "x",
                                    "comentario": "", "session_count": 1, "operation_count": 0,
                                    "session_id": "x", "interface": "TUI"}) + "\n")
        session_data = {"total_sessoes_all_time": 1, "total_operacoes_all_time": 0, "session_id": "x", "interface": "TUI"}
        (tmp / "session.json").write_text(json.dumps(session_data), encoding="utf-8")
        with patch('builtins.input', side_effect=['10', '', '', '']), \
             patch('builtins.print') as mp, \
             patch('foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service.BootstrapService.get_user_config_dir', return_value=tmp):
            handler = MenuConfigHandler(self.menu)
            handler._pesquisa_nps_ui()
        printed = "".join(c.args[0] for c in mp.call_args_list if c.args)
        self.assertIn("Últimas avaliações", printed)

    def test_nps_export_option_displayed(self):
        """'Exportar para Email' option must appear after response."""
        from foton_system.interfaces.cli.menus_config import MenuConfigHandler
        import tempfile, pathlib, json
        tmp = pathlib.Path(tempfile.mkdtemp())
        session_data = {"total_sessoes_all_time": 1, "total_operacoes_all_time": 0, "session_id": "x", "interface": "TUI"}
        (tmp / "session.json").write_text(json.dumps(session_data), encoding="utf-8")
        with patch('builtins.input', side_effect=['9', '', '', 's', '']), \
             patch('builtins.print') as mp, \
             patch('foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service.BootstrapService.get_user_config_dir', return_value=tmp), \
             patch('foton_system.interfaces.cli.menus_config.MenuConfigHandler._exportar_nps_zip') as mock_export:
            handler = MenuConfigHandler(self.menu)
            handler._pesquisa_nps_ui()
        printed = "".join(c.args[0] for c in mp.call_args_list if c.args)
        self.assertIn("Exportar", printed)

    def test_nps_export_creates_zip(self):
        """Export generates .zip with NPS report + operation_log + session."""
        from foton_system.interfaces.cli.menus_config import MenuConfigHandler
        import tempfile, pathlib, json, os, zipfile
        tmp = pathlib.Path(tempfile.mkdtemp())
        session_file = tmp / "session.json"
        session_file.write_text(json.dumps({"session_id": "s1", "interface": "TUI"}), encoding="utf-8")
        nps_file = tmp / "nps_responses.jsonl"
        nps_file.write_text(json.dumps({"score": 9, "classification": "Promotor", "comentario": "Bom"}) + "\n", encoding="utf-8")
        op_file = tmp / "operation_log.jsonl"
        op_file.write_text(json.dumps({"operacao": "teste"}) + "\n", encoding="utf-8")
        desktop = pathlib.Path(tempfile.mkdtemp())
        handler = MenuConfigHandler(self.menu)
        with patch('foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service.BootstrapService.get_user_config_dir', return_value=tmp), \
             patch('pathlib.Path.home', return_value=desktop.parent):
            result = handler._exportar_nps_zip()
        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(result))
        self.assertTrue(result.endswith(".zip"))
        with zipfile.ZipFile(result, 'r') as zf:
            names = [n.lower() for n in zf.namelist()]
            self.assertTrue(any("nps" in n for n in names))
            self.assertTrue(any("operation_log" in n for n in names))
            self.assertTrue(any("session" in n for n in names))

    def test_nps_export_no_http(self):
        """Export must NOT make any HTTP requests."""
        from foton_system.interfaces.cli.menus_config import MenuConfigHandler
        import tempfile, pathlib, json, os
        tmp = pathlib.Path(tempfile.mkdtemp())
        session_file = tmp / "session.json"
        session_file.write_text(json.dumps({"session_id": "s1", "interface": "TUI"}), encoding="utf-8")
        nps_file = tmp / "nps_responses.jsonl"
        nps_file.write_text(json.dumps({"score": 9, "classification": "Promotor"}) + "\n", encoding="utf-8")
        op_file = tmp / "operation_log.jsonl"
        op_file.write_text(json.dumps({"operacao": "teste"}) + "\n", encoding="utf-8")
        handler = MenuConfigHandler(self.menu)
        with patch('foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service.BootstrapService.get_user_config_dir', return_value=tmp), \
             patch('pathlib.Path.home', return_value=pathlib.Path(tempfile.mkdtemp()).parent), \
             patch('urllib.request.urlopen') as mock_http:
            handler._exportar_nps_zip()
        mock_http.assert_not_called()

    def test_export_dados_uso_option_in_settings(self):
        """'Exportar Dados de Uso' must appear in Config menu."""
        with patch('builtins.input', side_effect=['7', '0', '0']), \
             patch('builtins.print') as mock_print, \
             patch('foton_system.interfaces.cli.views.tui_layout.TUILayout.clear'):
            with self.assertRaises(SystemExit):
                self.menu.run()
            printed = "".join([call.args[0] for call in mock_print.call_args_list if call.args])
        self.assertIn("Exportar Dados de Uso", printed)


    # ----- STORY-045: RULE-UX-8.11 cp1252 compatibility -----
    def test_cp1252_compatibility_menus_config(self):
        """Every char in menus_config.py must be cp1252-safe (zero emoji)."""
        import inspect
        import foton_system.interfaces.cli.menus_config as mod
        source = inspect.getsource(mod)
        for line_no, line in enumerate(source.split('\n'), 1):
            for char in line:
                try:
                    char.encode("cp1252")
                except UnicodeEncodeError:
                    self.fail(f"Char U+{ord(char):04X} at menus_config.py:{line_no} "
                              f"is not cp1252-safe ({line.strip()[:50]})")

    def test_cp1252_compatibility_menus_docs(self):
        """Every char in menus_docs.py must be cp1252-safe (zero emoji)."""
        import inspect
        import foton_system.interfaces.cli.menus_docs as mod
        source = inspect.getsource(mod)
        for line_no, line in enumerate(source.split('\n'), 1):
            for char in line:
                try:
                    char.encode("cp1252")
                except UnicodeEncodeError:
                    self.fail(f"Char U+{ord(char):04X} at menus_docs.py:{line_no} "
                              f"is not cp1252-safe ({line.strip()[:50]})")

    def test_nps_trend_ascii(self):
        """NPS trend must use ASCII-safe [+] / [-] / [=] instead of emojis."""
        from foton_system.interfaces.cli.menus_config import MenuConfigHandler
        import tempfile, pathlib, json
        tmp = pathlib.Path(tempfile.mkdtemp())
        nps_file = tmp / "nps_responses.jsonl"
        for s in [5, 7, 9]:
            with open(nps_file, "a", encoding="utf-8") as f:
                f.write(json.dumps({"score": s, "timestamp": "2026-01-01T00:00:00",
                                    "classification": "x", "comentario": "",
                                    "session_count": 1, "operation_count": 0,
                                    "session_id": "x", "interface": "TUI"}) + "\n")
        session_data = {"total_sessoes_all_time": 1, "total_operacoes_all_time": 0,
                        "session_id": "x", "interface": "TUI"}
        (tmp / "session.json").write_text(json.dumps(session_data), encoding="utf-8")
        with patch('builtins.input', side_effect=['10', '', '', '']), \
             patch('builtins.print') as mp, \
             patch('foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service.BootstrapService.get_user_config_dir', return_value=tmp):
            handler = MenuConfigHandler(self.menu)
            handler._pesquisa_nps_ui()
        printed = "".join(c.args[0] for c in mp.call_args_list if c.args)
        self.assertIn("[+]", printed)


if __name__ == '__main__':
    unittest.main()
