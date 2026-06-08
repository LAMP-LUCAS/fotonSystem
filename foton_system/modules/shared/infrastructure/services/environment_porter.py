"""
EnvironmentPorter: O "Porteiro" do sistema.
Identifica o ambiente de execução (SO, GUI, Docker, WSL, MCP) e define o perfil de uso e capacidades.
"""

import os
import sys
import platform
import logging
import shutil
import subprocess
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

class SystemProfile(Enum):
    SERVER_HEADLESS = "SERVER_HEADLESS"    # Sem interface gráfica, focado em CLI/MCP/Docker
    DESKTOP_GUI = "DESKTOP_GUI"            # Interface gráfica nativa completa
    DESKTOP_WSL = "DESKTOP_WSL"            # Windows Subsystem for Linux (pode ter GUI via GWSL/X11)
    DESKTOP_TUI = "DESKTOP_TUI"            # Desktop sem display ou preferência por terminal
    MOCK = "MOCK"                          # Para testes unitários

class EnvironmentPorter:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EnvironmentPorter, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self._detect_environment()
        self._initialized = True

    def _detect_environment(self):
        """Detecta SO, GUI, Docker, WSL e MCP."""
        self.os_type = platform.system().lower()  # 'windows', 'linux', 'darwin'
        self.is_frozen = getattr(sys, 'frozen', False)
        
        # 1. Detecção de Docker
        self.is_docker = self._check_docker()
        
        # 2. Detecção de WSL
        self.is_wsl = self._check_wsl()
        
        # 3. Detecção de GUI
        self.has_gui = self._check_gui_availability()
        
        # 4. Detecção de MCP
        self.is_mcp_mode = "--mcp" in sys.argv
        
        # 5. Definição do Perfil Principal
        if self.is_docker:
            self.profile = SystemProfile.SERVER_HEADLESS
        elif self.is_wsl:
            self.profile = SystemProfile.DESKTOP_WSL
        elif not self.has_gui:
            self.profile = SystemProfile.SERVER_HEADLESS
        else:
            self.profile = SystemProfile.DESKTOP_GUI
            
        # Nota: O perfil pode ser forçado via configuração (Futuro)
        
        logger.info(f"Ambiente detectado: OS={self.os_type}, Profile={self.profile.value}, GUI={self.has_gui}, Docker={self.is_docker}, WSL={self.is_wsl}")

    def _check_docker(self) -> bool:
        """Verifica se está rodando dentro de um container Docker."""
        # Verificações padrão
        if os.path.exists('/.dockerenv') or os.path.exists('/.dockerinit'):
            return True
        
        # Verificação via cgroup
        try:
            with open('/proc/1/cgroup', 'rt') as f:
                if 'docker' in f.read():
                    return True
        except (IOError, OSError):
            pass
            
        # Variáveis de ambiente comuns
        if os.environ.get('DOCKER_HOST') or os.environ.get('DOTNET_RUNNING_IN_CONTAINER'):
            return True
            
        return False

    def _check_wsl(self) -> bool:
        """Verifica se está rodando no WSL."""
        if self.os_type != 'linux':
            return False
        
        try:
            with open('/proc/version', 'r') as f:
                version_info = f.read().lower()
                return 'microsoft' in version_info or 'wsl' in version_info
        except (IOError, OSError):
            return False

    def _check_gui_availability(self) -> bool:
        """Verifica se há um servidor gráfico funcional disponível."""
        if self.os_type == 'windows':
            # Assume GUI no Windows (exceto se detectarmos explicitamente modo server sem shell)
            return True
        elif self.os_type == 'darwin': # macOS
            return True
        elif self.os_type == 'linux':
            # Verifica variável de ambiente de display
            display = os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')
            if not display:
                return False
                
            # No Linux, verifica também o socket X11 (sugestão da auditoria)
            # Geralmente /tmp/.X11-unix/X0, X1, etc.
            x11_socket_dir = Path("/tmp/.X11-unix")
            if x11_socket_dir.exists():
                sockets = list(x11_socket_dir.glob("X*"))
                if sockets:
                    return True
            
            # Se tem DISPLAY mas não achou socket, pode ser um túnel SSH ou Wayland puro
            return True
            
        return False

    def can_use_feature(self, feature_name: str) -> bool:
        """
        Verifica se uma feature específica é suportada no ambiente atual.
        Centraliza a lógica de 'Feature Toggles'.
        """
        features = {
            "webview": self.has_gui and not self.is_mcp_mode and self._check_webview_installed(),
            "native_dialogs": self.has_gui and self._has_dialog_tools(),
            "shortcuts": self.profile == SystemProfile.DESKTOP_GUI and self.os_type == "windows",
            "watcher": True,
            "rag": True,
            "tui": sys.stdout.isatty() or self.is_mcp_mode
        }
        return features.get(feature_name, False)

    def _check_webview_installed(self) -> bool:
        """Verifica se a biblioteca pywebview está disponível sem causar crash global."""
        try:
            import importlib.util
            return importlib.util.find_spec("webview") is not None
        except ImportError:
            return False

    def _has_dialog_tools(self) -> bool:
        """Verifica se ferramentas de diálogo nativo (zenity, kdialog) estão presentes no Linux."""
        if self.os_type == 'windows' or self.os_type == 'darwin':
            return True # Windows/Mac usam APIs nativas ou Tkinter
            
        # No Linux, verificamos utilitários comuns
        return any(shutil.which(tool) for tool in ['zenity', 'kdialog', 'gxmessage'])

    def get_summary(self) -> str:
        """Retorna um resumo amigável do ambiente para debug/logs."""
        caps = []
        if self.has_gui: caps.append("GUI")
        if self.is_docker: caps.append("Docker")
        if self.is_wsl: caps.append("WSL")
        if self.is_mcp_mode: caps.append("MCP")
        
        cap_str = f" [{', '.join(caps)}]" if caps else ""
        return f"FotonProfile: {self.profile.value}{cap_str} on {self.os_type.capitalize()}"

    def get_integrator(self):
        """Retorna o adaptador de integração com o SO adequado."""
        if self.profile == SystemProfile.SERVER_HEADLESS:
            from foton_system.modules.shared.infrastructure.adapters.system.null_integrator import NullIntegrator
            return NullIntegrator()
        
        if self.os_type == 'windows':
            from foton_system.modules.shared.infrastructure.adapters.system.windows_integrator import WindowsIntegrator
            return WindowsIntegrator()
        elif self.os_type == 'linux':
            from foton_system.modules.shared.infrastructure.adapters.system.linux_integrator import LinuxIntegrator
            return LinuxIntegrator()
        
        from foton_system.modules.shared.infrastructure.adapters.system.null_integrator import NullIntegrator
        return NullIntegrator()

    def get_form_filler(self):
        """Retorna o preenchedor de formulários adequado ao ambiente."""
        if self.profile == SystemProfile.SERVER_HEADLESS:
            from foton_system.modules.shared.infrastructure.adapters.forms.tui_form_adapter import TuiFormAdapter
            return TuiFormAdapter()
            
        if self.can_use_feature("webview"):
            from foton_system.modules.shared.infrastructure.adapters.forms.webview_form_adapter import WebViewFormAdapter
            return WebViewFormAdapter()
        else:
            from foton_system.modules.shared.infrastructure.adapters.forms.browser_form_adapter import BrowserFormAdapter
            return BrowserFormAdapter()

# Helper para uso simplificado
def get_porter() -> EnvironmentPorter:
    return EnvironmentPorter()

if __name__ == "__main__":
    # Teste rápido
    porter = EnvironmentPorter()
    print(porter.get_summary())
    print(f"Pode usar WebView? {porter.can_use_feature('webview')}")
    print(f"Pode usar Diálogos? {porter.can_use_feature('native_dialogs')}")
