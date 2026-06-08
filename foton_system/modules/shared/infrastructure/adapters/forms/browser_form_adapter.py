import webbrowser
import logging
from typing import Callable
from pathlib import Path
from foton_system.modules.shared.application.ports.form_interface_port import FormInterfacePort

logger = logging.getLogger(__name__)


class BrowserFormAdapter(FormInterfacePort):
    """Adapter que abre o formulário no navegador padrão do sistema."""

    def open_form(self, initial_content: str, save_callback: Callable[[str], bool]) -> bool:
        """Abre o formulário de preenchimento no navegador padrão."""
        try:
            from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
            html_path: Path = PathManager.get_assets_dir() / "fotonInfoInterface.html"

            if not html_path.exists():
                html_path = Path(__file__).resolve().parents[4] / "interfaces" / "fotonInfoInterface.html"

            if html_path.exists():
                webbrowser.open(f"file:///{html_path.resolve()}")
                print("\n✅ Interface aberta no navegador.")
                print("📝 Nota: No modo navegador, você deve copiar o resultado final manualmente e salvar no arquivo.")
                return True

            return False
        except Exception as e:
            logger.error(f"Erro ao abrir browser: {e}")
            return False
