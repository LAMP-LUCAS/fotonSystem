import os
import subprocess
from pathlib import Path
from foton_system.modules.shared.application.ports.system_integrator_port import SystemIntegratorPort


class LinuxIntegrator(SystemIntegratorPort):
    """Integração com desktop Linux — atalhos .desktop e xdg-open."""

    def create_shortcut(self, target_path: Path, app_name: str, description: str = "") -> bool:
        """Cria um arquivo .desktop no menu de aplicações do usuário."""
        desktop_file_content: str = f"""[Desktop Entry]
Type=Application
Name={app_name}
Comment={description}
Exec={target_path}
Icon={target_path.parent}/foton.svg
Terminal=true
Categories=Office;Development;
"""
        try:
            apps_dir: Path = Path.home() / ".local" / "share" / "applications"
            apps_dir.mkdir(parents=True, exist_ok=True)

            file_path: Path = apps_dir / f"{app_name.lower().replace(' ', '_')}.desktop"
            file_path.write_text(desktop_file_content, encoding="utf-8")
            file_path.chmod(0o755)
            return True
        except Exception:
            return False

    def open_external(self, path: Path) -> bool:
        """Abre arquivo ou URL no visualizador padrão do sistema."""
        try:
            subprocess.run(['xdg-open', str(path)], check=True)
            return True
        except Exception:
            return False
