"""
Tests for STORY-034: TUI RAG Configuration.

Covers:
- RULE-RAG-7.3: Exibir feasibility report
- RULE-RAG-9.4: Exibir warnings do pipeline validator
- RULE-RAG-12.3: Download com confirmacao e verificacao de disco
- RULE-RAG-12.4: Barra de progresso em tempo real durante download
"""

# @story: STORY-034
# @rule: RULE-RAG-7.3, RULE-RAG-9.4, RULE-RAG-12.3, RULE-RAG-12.4

import pytest
from unittest.mock import MagicMock, patch, PropertyMock


class TestMenuRagHandler:
    """Tests for MenuRagHandler initialization and menu navigation."""

    def test_handler_initialization(self):
        """MenuRagHandler should store reference to menu system (AC: 1)."""
        from foton_system.interfaces.cli.menus_rag import MenuRagHandler
        mock_menu = MagicMock()
        handler = MenuRagHandler(mock_menu)
        assert handler.menu is mock_menu

    def test_display_rag_menu_returns_choice(self):
        """display_rag_menu should call input and return the choice."""
        from foton_system.interfaces.cli.menus_rag import MenuRagHandler
        mock_menu = MagicMock()
        handler = MenuRagHandler(mock_menu)
        with patch('builtins.input', return_value='1'):
            assert handler.display_rag_menu() == '1'

    def test_display_rag_menu_shows_current_mode(self, capsys):
        """display_rag_menu should show the current embedding mode (AC: 1, 2)."""
        from foton_system.interfaces.cli.menus_rag import MenuRagHandler
        from foton_system.modules.shared.infrastructure.config.config import Config

        mock_menu = MagicMock()
        handler = MenuRagHandler(mock_menu)

        with patch('builtins.input', return_value='0'):
            with patch.object(Config, 'rag_config', new_callable=PropertyMock) as mock_rag:
                mock_rag.return_value = {
                    "mode": "bgem3",
                    "models": {"primary": "bgem3", "fallback": []},
                    "pipeline": {"type": "simple", "nodes": ["embed", "search", "format"]},
                }
                handler.display_rag_menu()
                captured = capsys.readouterr()
                assert "BGE-M3" in captured.out

    def test_handle_rag_config_zero_exits(self):
        """handle_rag_config should break loop on '0' (AC: 1)."""
        from foton_system.interfaces.cli.menus_rag import MenuRagHandler
        mock_menu = MagicMock()
        handler = MenuRagHandler(mock_menu)
        with patch.object(handler, 'display_rag_menu', return_value='0'):
            handler.handle_rag_config()

    def test_handle_rag_config_invalid_choice_shows_error(self):
        """handle_rag_config should show error on invalid choice."""
        from foton_system.interfaces.cli.menus_rag import MenuRagHandler
        mock_menu = MagicMock()
        handler = MenuRagHandler(mock_menu)
        with patch.object(handler, 'display_rag_menu', side_effect=['x', '0']):
            handler.handle_rag_config()
            mock_menu.print_error.assert_called_once()


class TestMenuRagShowDiagnostics:
    """Tests for diagnostics display (AC: 2, 7)."""

    def test_show_diagnostics_displays_hardware(self, capsys):
        """show_diagnostics should display CPU, RAM, GPU info (AC: 2)."""
        from foton_system.interfaces.cli.menus_rag import MenuRagHandler

        mock_menu = MagicMock()
        handler = MenuRagHandler(mock_menu)

        mock_profile = MagicMock()
        mock_profile.cpu_cores = 8
        mock_profile.ram_total_gb = 16.0
        mock_profile.ram_available_gb = 10.5
        mock_profile.has_cuda = True
        mock_profile.cuda_version = "12.1"
        mock_profile.vram_gb = 6.0
        mock_profile.disk_free_gb = 50.0
        mock_profile.has_mps = False

        with patch('foton_system.core.rag.hardware_profiler.HardwareProfiler.detect',
                   return_value=mock_profile):
            with patch('foton_system.core.memory.vector_store.VectorStoreManager') as MockVSM:
                mock_vsm = MagicMock()
                mock_vsm.diagnostic.return_value = {"mode": "minilm", "stores": {}}
                MockVSM.return_value = mock_vsm
                handler.show_diagnostics()
                captured = capsys.readouterr()
                assert "8" in captured.out
                assert "16.0" in captured.out
                assert "CUDA" in captured.out or "12.1" in captured.out

    def test_show_diagnostics_displays_collections(self, capsys):
        """show_diagnostics should show chunks, CB status, last index (AC: 7)."""
        from foton_system.interfaces.cli.menus_rag import MenuRagHandler

        mock_menu = MagicMock()
        handler = MenuRagHandler(mock_menu)

        mock_profile = MagicMock()
        mock_profile.cpu_cores = 4
        mock_profile.ram_total_gb = 8.0
        mock_profile.ram_available_gb = 4.0
        mock_profile.has_cuda = False
        mock_profile.has_mps = False
        mock_profile.disk_free_gb = 30.0

        mock_diag = {
            "mode": "minilm",
            "stores": {
                "minilm": {
                    "total_chunks": 42,
                    "circuit_breaker_status": "CLOSED",
                    "ultima_indexacao": "2026-07-02 10:00:00",
                    "model_tag": "minilm",
                    "model_name": "MiniLM",
                    "collection_name": "foton_minilm_384d",
                }
            },
        }

        with patch('foton_system.core.rag.hardware_profiler.HardwareProfiler.detect',
                   return_value=mock_profile):
            with patch('foton_system.core.memory.vector_store.VectorStoreManager') as MockVSM:
                mock_vsm = MagicMock()
                mock_vsm.diagnostic.return_value = mock_diag
                MockVSM.return_value = mock_vsm
                handler.show_diagnostics()
                captured = capsys.readouterr()
                assert "42" in captured.out
                assert "CLOSED" in captured.out
                assert "2026-07-02" in captured.out
                assert "MiniLM" in captured.out


class TestMenuRagModelStatus:
    """Tests for model status display (AC: 3)."""

    def test_show_model_status_lists_models(self, capsys):
        """show_model_status should list all models with install status (AC: 3)."""
        from foton_system.interfaces.cli.menus_rag import MenuRagHandler

        mock_menu = MagicMock()
        handler = MenuRagHandler(mock_menu)

        mock_entry_minilm = MagicMock()
        mock_entry_minilm.id = "minilm"
        mock_entry_minilm.name = "paraphrase-multilingual-MiniLM-L12-v2"
        mock_entry_minilm.type = "embedding"
        mock_entry_minilm.dimensions = 384
        mock_entry_minilm.ram_required_gb = 1.0
        mock_entry_minilm.disk_required_gb = 0.5
        mock_entry_minilm.requires_gpu = False
        mock_entry_minilm.is_default = True

        mock_entry_bgem3 = MagicMock()
        mock_entry_bgem3.id = "bgem3"
        mock_entry_bgem3.name = "BAAI/bge-m3"
        mock_entry_bgem3.type = "embedding"
        mock_entry_bgem3.dimensions = 1024
        mock_entry_bgem3.ram_required_gb = 4.5
        mock_entry_bgem3.disk_required_gb = 2.5
        mock_entry_bgem3.requires_gpu = False
        mock_entry_bgem3.is_default = False

        with patch('foton_system.core.rag.model_registry.ModelRegistry') as MockReg:
            mock_reg = MagicMock()
            mock_reg.list_models.return_value = [mock_entry_minilm, mock_entry_bgem3]
            mock_reg.is_installed.side_effect = lambda mid: mid == "minilm"
            MockReg.return_value = mock_reg
            handler.show_model_status()
            captured = capsys.readouterr()
            assert "minilm" in captured.out
            assert "384" in captured.out
            assert "Instalado" in captured.out or "instalado" in captured.out
            assert "bgem3" in captured.out


class TestMenuRagChangeMode:
    """Tests for mode switching (AC: 4, 5, 8, 9, 10)."""

    def test_change_mode_same_mode_returns_early(self):
        """Changing to current mode should return without changes (AC: 8)."""
        from foton_system.interfaces.cli.menus_rag import MenuRagHandler
        from foton_system.modules.shared.infrastructure.config.config import Config

        mock_menu = MagicMock()
        handler = MenuRagHandler(mock_menu)

        with patch.object(Config, 'rag_config', new_callable=PropertyMock) as mock_rag:
            mock_rag.return_value = {"mode": "minilm", "models": {"primary": "minilm", "fallback": []},
                                      "pipeline": {"type": "simple", "nodes": ["embed", "search", "format"]}}
            with patch('builtins.input', return_value='1'):
                handler.show_change_mode_menu()
                mock_menu.print_info.assert_called_once()

    def test_change_mode_valid_updates_config(self):
        """Changing to a valid new mode should persist config (AC: 4, 8)."""
        from foton_system.interfaces.cli.menus_rag import MenuRagHandler
        from foton_system.modules.shared.infrastructure.config.config import Config

        mock_menu = MagicMock()
        mock_menu.confirm_action.return_value = False
        handler = MenuRagHandler(mock_menu)

        mock_profile = MagicMock()
        mock_profile.ram_total_gb = 16.0
        mock_profile.ram_available_gb = 10.0
        mock_profile.has_cuda = False
        mock_profile.has_mps = False
        mock_profile.disk_free_gb = 100.0

        with patch.object(Config, 'rag_config', new_callable=PropertyMock) as mock_rag:
            mock_rag.return_value = {"mode": "minilm", "models": {"primary": "minilm", "fallback": []},
                                      "pipeline": {"type": "simple", "nodes": ["embed", "search", "format"]}}
            with patch('foton_system.core.rag.hardware_profiler.HardwareProfiler.detect',
                       return_value=mock_profile):
                with patch('foton_system.core.rag.model_registry.ModelRegistry') as MockReg:
                    mock_reg = MagicMock()
                    mock_reg.is_installed.return_value = True
                    mock_reg.list_models.return_value = []
                    MockReg.return_value = mock_reg
                    with patch.object(Config, 'set') as mock_set:
                        with patch.object(Config, 'save') as mock_save:
                            with patch('builtins.input', return_value='2'):
                                handler.show_change_mode_menu()
                                mock_set.assert_called_once()
                                mock_save.assert_called_once()

    def test_change_mode_with_warning_shows_warning(self, capsys):
        """Mode with insufficient hardware should show warning (AC: 10, RULE-RAG-7.3)."""
        from foton_system.interfaces.cli.menus_rag import MenuRagHandler
        from foton_system.modules.shared.infrastructure.config.config import Config

        mock_menu = MagicMock()
        mock_menu.confirm_action.return_value = False
        handler = MenuRagHandler(mock_menu)

        mock_profile = MagicMock()
        mock_profile.ram_total_gb = 6.0
        mock_profile.ram_available_gb = 3.0
        mock_profile.has_cuda = False
        mock_profile.has_mps = False
        mock_profile.disk_free_gb = 50.0

        with patch.object(Config, 'rag_config', new_callable=PropertyMock) as mock_rag:
            mock_rag.return_value = {"mode": "minilm", "models": {"primary": "minilm", "fallback": []},
                                      "pipeline": {"type": "simple", "nodes": ["embed", "search", "format"]}}
            with patch('foton_system.core.rag.hardware_profiler.HardwareProfiler.detect',
                       return_value=mock_profile):
                with patch('foton_system.core.rag.model_router.ModelRouter.validate_pipeline_feasibility',
                           return_value=["RAM insuficiente para modo dual (min 8GB)"]):
                    with patch('builtins.input', return_value='3'):
                        handler.show_change_mode_menu()
                        captured = capsys.readouterr()
                        assert "insuficiente" in captured.out.lower() or "8GB" in captured.out

    def test_change_mode_triggers_download_when_not_installed(self, capsys):
        """Changing to mode with uninstalled model should trigger download (AC: 5, RULE-RAG-12.3)."""
        from foton_system.interfaces.cli.menus_rag import MenuRagHandler
        from foton_system.modules.shared.infrastructure.config.config import Config

        mock_menu = MagicMock()
        mock_menu.confirm_action.side_effect = [True, True, True]
        mock_menu.print_success.side_effect = lambda msg: print(msg)
        mock_menu.print_info.side_effect = lambda msg: print(msg)
        mock_menu.print_error.side_effect = lambda msg: print(msg)
        mock_menu.print_warning.side_effect = lambda msg: print(msg)
        handler = MenuRagHandler(mock_menu)

        mock_profile = MagicMock()
        mock_profile.ram_total_gb = 16.0
        mock_profile.ram_available_gb = 10.0
        mock_profile.has_cuda = False
        mock_profile.has_mps = False
        mock_profile.disk_free_gb = 100.0

        with patch.object(Config, 'rag_config', new_callable=PropertyMock) as mock_rag:
            mock_rag.return_value = {"mode": "minilm", "models": {"primary": "minilm", "fallback": []},
                                      "pipeline": {"type": "simple", "nodes": ["embed", "search", "format"]}}
            with patch('foton_system.core.rag.hardware_profiler.HardwareProfiler.detect',
                       return_value=mock_profile):
                with patch('foton_system.core.rag.model_registry.ModelRegistry') as MockReg:
                    mock_reg = MagicMock()
                    mock_reg.is_installed.return_value = False
                    mock_entry = MagicMock()
                    mock_entry.id = "bgem3"
                    mock_entry.disk_required_gb = 2.5
                    mock_reg.get.return_value = mock_entry
                    mock_reg.list_models.return_value = [mock_entry]
                    MockReg.return_value = mock_reg

                    mock_report = MagicMock()
                    mock_report.success = True
                    mock_report.model_path = "/path/to/model"

                    with patch('foton_system.core.rag.download_manager.DownloadManager.ensure_model',
                               return_value=mock_report) as mock_dl:
                        with patch.object(Config, 'set'):
                            with patch.object(Config, 'save'):
                                with patch('builtins.input', return_value='2'):
                                    handler.show_change_mode_menu()
                                    assert mock_dl.called
                                    captured = capsys.readouterr()
                                    assert "instalado" in captured.out.lower() or "sucesso" in captured.out.lower()


class TestMenuRagReindex:
    """Tests for reindex action (AC: 6, 9)."""

    def test_reindex_calls_op_index_knowledge(self):
        """Re-indexar should call OpIndexKnowledge.execute() (AC: 6)."""
        from foton_system.interfaces.cli.menus_rag import MenuRagHandler

        mock_menu = MagicMock()
        mock_menu.confirm_action.return_value = True
        handler = MenuRagHandler(mock_menu)

        with patch('builtins.input', return_value=''):
            with patch('foton_system.core.ops.op_index_knowledge.OpIndexKnowledge') as MockOp:
                mock_op = MagicMock()
                mock_op.execute.return_value = {"files_scanned": 15, "chunks_created": 120}
                MockOp.return_value = mock_op
                handler.reindex_knowledge_base()
                mock_op.execute.assert_called_once()

    def test_reindex_with_client_filter(self):
        """Re-indexar should pass client name when provided (AC: 6)."""
        from foton_system.interfaces.cli.menus_rag import MenuRagHandler

        mock_menu = MagicMock()
        mock_menu.confirm_action.return_value = True
        handler = MenuRagHandler(mock_menu)

        with patch('builtins.input', return_value='ClienteX'):
            with patch('foton_system.core.ops.op_index_knowledge.OpIndexKnowledge') as MockOp:
                mock_op = MagicMock()
                mock_op.execute.return_value = {"files_scanned": 5, "chunks_created": 30}
                MockOp.return_value = mock_op
                handler.reindex_knowledge_base()
                mock_op.execute.assert_called_once_with(cliente="ClienteX")


class TestMenuRagIntegration:
    """Tests for integration with menus.py and menus_config.py."""

    def test_option_8_in_settings_menu(self):
        """Settings menu should have option for RAG config (AC: 1)."""
        from foton_system.modules.shared.infrastructure.config.config import Config

        with patch('foton_system.modules.shared.infrastructure.config.config.Config.rag_config',
                   new_callable=PropertyMock) as mock_rag:
            mock_rag.return_value = {"mode": "minilm", "models": {"primary": "minilm", "fallback": []},
                                      "pipeline": {"type": "simple", "nodes": ["embed", "search", "format"]}}
            from foton_system.interfaces.cli.menus_config import MenuConfigHandler
            mock_menu = MagicMock()
            handler = MenuConfigHandler(mock_menu)

            with patch('builtins.input', return_value='8'):
                choice = handler.display_settings_menu(Config())
                assert choice == '8'

    def test_menu_rag_handler_api(self):
        """MenuRagHandler should expose all expected public methods."""
        from foton_system.interfaces.cli.menus_rag import MenuRagHandler
        from unittest.mock import MagicMock

        methods = [
            'handle_rag_config', 'display_rag_menu',
            'show_diagnostics', 'show_change_mode_menu',
            'reindex_knowledge_base', 'show_model_status',
            '_index_knowledge_ui', '_query_knowledge_ui',
        ]
        rag_handler = MenuRagHandler(MagicMock())
        for m in methods:
            assert hasattr(rag_handler, m), "Missing method: {}".format(m)

    def test_rag_ui_not_in_menus_config(self):
        """MenuConfigHandler should NOT have _index_knowledge_ui or _query_knowledge_ui."""
        from foton_system.interfaces.cli.menus_config import MenuConfigHandler
        from unittest.mock import MagicMock

        handler = MenuConfigHandler(MagicMock())
        assert not hasattr(handler, '_index_knowledge_ui'), "DEVE ser removido de MenuConfigHandler"
        assert not hasattr(handler, '_query_knowledge_ui'), "DEVE ser removido de MenuConfigHandler"

    def test_rag_ui_in_menus_rag(self):
        """MenuRagHandler should have _index_knowledge_ui and _query_knowledge_ui."""
        from foton_system.interfaces.cli.menus_rag import MenuRagHandler
        from unittest.mock import MagicMock

        handler = MenuRagHandler(MagicMock())
        assert hasattr(handler, '_index_knowledge_ui')
        assert hasattr(handler, '_query_knowledge_ui')
