import os
import sys
from pathlib import Path
from foton_system.modules.shared.application.ports.system_integrator_port import SystemIntegratorPort


class WindowsIntegrator(SystemIntegratorPort):
    """Integração com desktop Windows — atalhos .lnk e os.startfile."""

    def create_shortcut(self, target_path: Path, app_name: str, description: str = "") -> bool:
        """Cria atalhos no Desktop e Menu Iniciar do Windows."""
        try:
            import winshell
            from win32com.client import Dispatch

            target_path_str: str = str(target_path)
            work_dir: str = str(target_path.parent)

            shell = Dispatch('WScript.Shell')

            desktop: str = winshell.desktop()
            lnk_path: str = os.path.join(desktop, f"{app_name}.lnk")
            shortcut = shell.CreateShortCut(lnk_path)
            shortcut.Targetpath = target_path_str
            shortcut.WorkingDirectory = work_dir
            shortcut.IconLocation = target_path_str
            shortcut.Description = description
            shortcut.save()

            start_menu: str = winshell.programs()
            lnk_path = os.path.join(start_menu, f"{app_name}.lnk")
            shortcut = shell.CreateShortCut(lnk_path)
            shortcut.Targetpath = target_path_str
            shortcut.WorkingDirectory = work_dir
            shortcut.IconLocation = target_path_str
            shortcut.save()

            return True
        except Exception:
            return False

    def open_external(self, path: Path) -> bool:
        """Abre arquivo ou URL no visualizador padrão do Windows."""
        try:
            os.startfile(path)
            return True
        except Exception:
            return False
