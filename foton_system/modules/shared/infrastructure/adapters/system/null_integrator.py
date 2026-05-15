from pathlib import Path
from foton_system.modules.shared.application.ports.system_integrator_port import SystemIntegratorPort

class NullIntegrator(SystemIntegratorPort):
    def create_shortcut(self, target_path: Path, app_name: str, description: str = "") -> bool:
        # Silencioso em servidores
        return True

    def open_external(self, path: Path) -> bool:
        # Apenas loga ou ignora em servidores headless
        print(f"INFO: Tentativa de abrir recurso: {path}")
        return True
