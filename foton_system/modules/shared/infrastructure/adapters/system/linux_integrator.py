import os
import subprocess
from pathlib import Path
from foton_system.modules.shared.application.ports.system_integrator_port import SystemIntegratorPort

class LinuxIntegrator(SystemIntegratorPort):
    def create_shortcut(self, target_path: Path, app_name: str, description: str = "") -> bool:
        """Cria um arquivo .desktop para integração com menus Linux."""
        desktop_file_content = f"""[Desktop Entry]
Type=Application
Name={app_name}
Comment={description}
Exec={target_path}
Icon={target_path.parent}/foton.svg
Terminal=true
Categories=Office;Development;
"""
        try:
            # Caminho padrão para aplicações do usuário
            apps_dir = Path.home() / ".local" / "share" / "applications"
            apps_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = apps_dir / f"{app_name.lower().replace(' ', '_')}.desktop"
            file_path.write_text(desktop_file_content, encoding="utf-8")
            
            # Tenta dar permissão de execução
            file_path.chmod(0o755)
            
            return True
        except:
            return False

    def open_external(self, path: Path) -> bool:
        try:
            subprocess.run(['xdg-open', str(path)], check=True)
            return True
        except:
            return False
