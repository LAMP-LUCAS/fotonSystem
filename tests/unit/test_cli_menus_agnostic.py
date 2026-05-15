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
    mock_porter.can_use_feature.side_effect = lambda f: f not in ["webview", "shortcuts"]
    
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
        # Opção 3 (Webview) e 7 (Atalhos) NÃO devem ser chamadas
        calls = [call.args[1] for call in mock_tui.print_menu_option.call_args_list]
        
        assert "Preencher Ficha (Interface)" not in calls
        assert "Instalação / Atalhos" not in calls
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
