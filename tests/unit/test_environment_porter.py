import os
import sys
import pytest
from pathlib import Path
from foton_system.modules.shared.infrastructure.services.environment_porter import EnvironmentPorter, SystemProfile

def test_porter_singleton():
    """Verifica se o Porter é de fato um Singleton."""
    p1 = EnvironmentPorter()
    p2 = EnvironmentPorter()
    assert p1 is p2

def test_docker_detection(monkeypatch):
    """Simula ambiente Docker via existência de arquivo e variáveis."""
    # Reset singleton state if needed for testing different scenarios
    EnvironmentPorter._instance = None
    
    # Mock existence of /.dockerenv
    original_exists = os.path.exists
    def mock_exists(path):
        if path == '/.dockerenv':
            return True
        return original_exists(path)
    
    monkeypatch.setattr(os.path, "exists", mock_exists)
    
    porter = EnvironmentPorter()
    assert porter.is_docker is True
    assert porter.profile == SystemProfile.SERVER_HEADLESS

def test_wsl_detection(monkeypatch):
    """Simula ambiente WSL via /proc/version."""
    EnvironmentPorter._instance = None
    
    import builtins
    original_open = builtins.open
    def mock_open(file, *args, **kwargs):
        if file == '/proc/version':
            from io import StringIO
            return StringIO("Linux version 5.15.133.1-microsoft-standard-WSL2")
        return original_open(file, *args, **kwargs)
    
    monkeypatch.setattr(builtins, "open", mock_open)
    monkeypatch.setattr("platform.system", lambda: "Linux")
    
    porter = EnvironmentPorter()
    assert porter.is_wsl is True
    assert porter.profile == SystemProfile.DESKTOP_WSL

def test_gui_detection_linux_no_display(monkeypatch):
    """Simula Linux sem DISPLAY (Server Headless)."""
    EnvironmentPorter._instance = None
    
    monkeypatch.setenv("DISPLAY", "")
    monkeypatch.setenv("WAYLAND_DISPLAY", "")
    monkeypatch.setattr("platform.system", lambda: "Linux")
    # Garante que não é docker nem wsl
    monkeypatch.setattr(os.path, "exists", lambda p: False)
    
    porter = EnvironmentPorter()
    assert porter.has_gui is False
    assert porter.profile == SystemProfile.SERVER_HEADLESS

def test_can_use_feature_native_dialogs_linux_zenity(monkeypatch):
    """Verifica can_use_feature para diálogos nativos se zenity existir."""
    EnvironmentPorter._instance = None
    
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setattr("shutil.which", lambda tool: tool == "zenity")
    
    porter = EnvironmentPorter()
    assert porter.can_use_feature("native_dialogs") is True

def test_mcp_mode_detection(monkeypatch):
    """Verifica se detecta o modo MCP via argumentos de linha de comando."""
    EnvironmentPorter._instance = None
    
    monkeypatch.setattr(sys, "argv", ["foton.exe", "--mcp"])
    
    porter = EnvironmentPorter()
    assert porter.is_mcp_mode is True
    # Em modo MCP, webview deve ser False mesmo com GUI
    assert porter.can_use_feature("webview") is False
