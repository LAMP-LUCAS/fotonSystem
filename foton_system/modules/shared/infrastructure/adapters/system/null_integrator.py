from pathlib import Path
from foton_system.modules.shared.application.ports.system_integrator_port import SystemIntegratorPort


class NullIntegrator(SystemIntegratorPort):
    """Integração nula para ambientes headless/servidor — operações são silenciosas."""

    def create_shortcut(self, target_path: Path, app_name: str, description: str = "") -> bool:
        """Ignora criação de atalho em ambientes sem desktop."""
        return True

    def open_external(self, path: Path) -> bool:
        """Exibe mensagem informativa em vez de abrir recurso externo."""
        print(f"INFO: Tentativa de abrir recurso: {path}")
        return True
