import os
import sys
from pathlib import Path
from foton_system.modules.shared.application.ports.system_integrator_port import SystemIntegratorPort

class WindowsIntegrator(SystemIntegratorPort):
    def create_shortcut(self, target_path: Path, app_name: str, description: str = "") -> bool:
        try:
            import winshell
            from win32com.client import Dispatch

            target_path_str = str(target_path)
            work_dir = str(target_path.parent)
            
            shell = Dispatch('WScript.Shell')

            # Atalho Desktop
            desktop = winshell.desktop()
            lnk_path = os.path.join(desktop, f"{app_name}.lnk")
            shortcut = shell.CreateShortCut(lnk_path)
            shortcut.Targetpath = target_path_str
            shortcut.WorkingDirectory = work_dir
            shortcut.IconLocation = target_path_str
            shortcut.Description = description
            shortcut.save()
            
            # Atalho Menu Iniciar
            start_menu = winshell.programs()
            lnk_path = os.path.join(start_menu, f"{app_name}.lnk")
            shortcut = shell.CreateShortCut(lnk_path)
            shortcut.Targetpath = target_path_str
            shortcut.WorkingDirectory = work_dir
            shortcut.IconLocation = target_path_str
            shortcut.save()
            
            return True
        except Exception as e:
            # Em vez de logger global, poderíamos injetar logger ou apenas retornar False
            return False

    def open_external(self, path: Path) -> bool:
        try:
            os.startfile(path)
            return True
        except:
            return False
