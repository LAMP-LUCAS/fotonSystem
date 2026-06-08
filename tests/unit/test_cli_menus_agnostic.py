import sys
import pytest
from unittest.mock import MagicMock, patch
from foton_system.interfaces.cli.menus import MenuSystem
from foton_system.modules.shared.infrastructure.services.environment_porter import SystemProfile

@pytest.fixture
def mock_porter():
    with patch('foton_system.interfaces.cli.menus.get_porter') as mock:
        porter = MagicMock()
        mock.return_value = porter
        yield porter

def test_main_menu_hides_gui_options_on_server(mock_porter, monkeypatch):
    """Verifica se o menu principal oculta opções de GUI em perfil SERVER."""
    # Configura o porteiro para simular servidor sem GUI
    mock_porter.profile = SystemProfile.SERVER_HEADLESS
    mock_porter.can_use_feature.side_effect = lambda f: f not in ["webview"]
    
    # Mock do input para sair imediatamente
    monkeypatch.setattr('builtins.input', lambda _: '0')
    
    # Mock do UI Provider e Repositorios para não carregar nada pesado
    with patch('foton_system.interfaces.cli.menus.get_ui_provider'), \
         patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
         patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
         patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'), \
         patch('foton_system.interfaces.cli.menus.TUILayout') as mock_tui:
        
        menu = MenuSystem()
        menu.display_main_menu()
        
        # Verifica as chamadas ao TUILayout.print_menu_option
        # Opção 3 (Webview) NÃO deve ser chamada em SERVER_HEADLESS
        calls = [call.args[1] for call in mock_tui.print_menu_option.call_args_list]
        
        assert "Preencher Ficha (Interface)" not in calls
        assert "Instalação / Atalhos" in calls
        assert "Gerenciar Clientes" in calls

def test_main_menu_shows_all_options_on_desktop(mock_porter, monkeypatch):
    """Verifica se o menu principal exibe todas as opções em perfil DESKTOP."""
    mock_porter.profile = SystemProfile.DESKTOP_GUI
    mock_porter.can_use_feature.return_value = True
    
    monkeypatch.setattr('builtins.input', lambda _: '0')
    
    with patch('foton_system.interfaces.cli.menus.get_ui_provider'), \
         patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
         patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
         patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'), \
         patch('foton_system.interfaces.cli.menus.TUILayout') as mock_tui:
        
        menu = MenuSystem()
        menu.display_main_menu()
        
        calls = [call.args[1] for call in mock_tui.print_menu_option.call_args_list]
        
        assert "Preencher Ficha (Interface)" in calls
        assert "Instalação / Atalhos" in calls


def test_system_profile_imported_via_menus():
    from foton_system.interfaces.cli.menus import SystemProfile as SP
    assert SP is SystemProfile
    assert SP.SERVER_HEADLESS == SystemProfile.SERVER_HEADLESS


@patch('subprocess.run')
def test_open_workspace_folder_linux(mock_run, mock_porter, monkeypatch):
    monkeypatch.setattr(sys, 'platform', 'linux')
    monkeypatch.setattr('builtins.input', lambda _: '')

    config = MagicMock()
    config.workspace_path = '/home/user/foton'

    with patch('foton_system.interfaces.cli.menus.get_ui_provider'), \
         patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
         patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
         patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'), \
         patch('foton_system.interfaces.cli.menus.TUILayout'):
        menu = MenuSystem()
        menu._open_workspace_folder(config)
        mock_run.assert_called_once_with(['xdg-open', '/home/user/foton'], check=True)


@patch('subprocess.run')
def test_open_workspace_folder_mac(mock_run, mock_porter, monkeypatch):
    monkeypatch.setattr(sys, 'platform', 'darwin')
    monkeypatch.setattr('builtins.input', lambda _: '')

    config = MagicMock()
    config.workspace_path = '/Users/lucas/foton'

    with patch('foton_system.interfaces.cli.menus.get_ui_provider'), \
         patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
         patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
         patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'), \
         patch('foton_system.interfaces.cli.menus.TUILayout'):
        menu = MenuSystem()
        menu._open_workspace_folder(config)
        mock_run.assert_called_once_with(['open', '/Users/lucas/foton'], check=True)


@patch('foton_system.interfaces.cli.menus.os.startfile')
def test_open_workspace_folder_windows(mock_startfile, mock_porter, monkeypatch):
    monkeypatch.setattr(sys, 'platform', 'win32')
    monkeypatch.setattr('builtins.input', lambda _: '')

    config = MagicMock()
    config.workspace_path = 'C:\\Users\\Lucas\\foton'

    with patch('foton_system.interfaces.cli.menus.get_ui_provider'), \
         patch('foton_system.interfaces.cli.menus.ExcelClientRepository'), \
         patch('foton_system.interfaces.cli.menus.PythonDocxAdapter'), \
         patch('foton_system.interfaces.cli.menus.PythonPPTXAdapter'), \
         patch('foton_system.interfaces.cli.menus.TUILayout'):
        menu = MenuSystem()
        menu._open_workspace_folder(config)
        mock_startfile.assert_called_once_with('C:\\Users\\Lucas\\foton')
