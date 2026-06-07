import logging
from typing import Callable
from foton_system.modules.shared.application.ports.form_interface_port import FormInterfacePort

logger = logging.getLogger(__name__)


class TuiFormAdapter(FormInterfacePort):
    """Adapter que instrui o usuário a editar o arquivo manualmente no modo servidor."""

    def open_form(self, initial_content: str, save_callback: Callable[[str], bool]) -> bool:
        """Exibe instruções para edição manual no terminal."""
        print("\n--- MODO TERMINAL (SERVER) ---")
        print("Preenchimento interativo não disponível via TUI nesta versão.")
        print("Por favor, edite o arquivo .md manualmente no servidor.")
        return True
