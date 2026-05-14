from abc import ABC, abstractmethod
from typing import Callable, Optional

class FormInterfacePort(ABC):
    """
    Interface para captura de dados rica (Formulários).
    """

    @abstractmethod
    def open_form(self, initial_content: str, save_callback: Callable[[str], bool]) -> bool:
        """Abre o formulário e retorna True se carregado com sucesso."""
        pass
