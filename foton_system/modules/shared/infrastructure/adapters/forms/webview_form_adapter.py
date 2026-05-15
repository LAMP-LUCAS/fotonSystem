import logging
from typing import Callable
from pathlib import Path
from foton_system.modules.shared.application.ports.form_interface_port import FormInterfacePort

logger = logging.getLogger(__name__)

class WebViewFormAdapter(FormInterfacePort):
    def open_form(self, initial_content: str, save_callback: Callable[[str], bool]) -> bool:
        try:
            import webview
            from foton_system.interfaces.webview_bridge import WebViewBridge
            
            # Localizar o arquivo HTML
            html_path = Path(__file__).resolve().parents[4] / "interfaces" / "fotonInfoInterface.html"
            
            if not html_path.exists():
                 from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
                 html_path = PathManager.get_assets_dir() / "fotonInfoInterface.html"

            if not html_path.exists():
                return False

            api = WebViewBridge(initial_content, save_callback)
            
            window = webview.create_window(
                'Foton System - Preenchedor de Templates',
                str(html_path),
                js_api=api,
                width=1000,
                height=800,
                resizable=True
            )
            api.window = window
            webview.start()
            return True
        except ImportError:
            logger.warning("WebView não instalado. Fallback necessário.")
            return False
        except Exception as e:
            logger.error(f"Falha ao iniciar WebView: {e}")
            return False
