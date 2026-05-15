from abc import ABC, abstractmethod
from pathlib import Path

class SystemIntegratorPort(ABC):
    """
    Porta para integrações específicas de Sistema Operacional.
    """
    
    @abstractmethod
    def create_shortcut(self, target_path: Path, app_name: str, description: str = "") -> bool:
        """Cria atalhos no desktop/menu iniciar."""
        pass

    @abstractmethod
    def open_external(self, path: Path) -> bool:
        """Abre um arquivo ou pasta no aplicativo padrão do SO."""
        pass
