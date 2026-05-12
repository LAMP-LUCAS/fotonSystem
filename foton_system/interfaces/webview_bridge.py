"""
WebViewBridge - Ponte entre Python e Interface HTML (FotonInfoInterface).

Utiliza pywebview para abrir a interface de preenchimento de dados de forma nativa.
Permite ler arquivos MD do projeto e salvar o resultado diretamente no sistema.
"""

import webview
import json
import os
import sys
from pathlib import Path
from typing import Optional

class WebViewBridge:
    def __init__(self, initial_md_content: str = "", save_callback=None):
        self.initial_md_content = initial_md_content
        self.save_callback = save_callback
        self.window = None

    def get_initial_content(self):
        """Retorna o conteúdo MD inicial para o JS."""
        return self.initial_md_content

    def save_markdown(self, content: str):
        """Chamado pelo JS para salvar o arquivo final."""
        if self.save_callback:
            success = self.save_callback(content)
            if success:
                return {"status": "success", "message": "Arquivo salvo com sucesso!"}
            return {"status": "error", "message": "Falha ao salvar arquivo no backend."}
        return {"status": "info", "message": "Simulação: Arquivo recebido pelo backend."}

    def close(self):
        """Fecha a janela."""
        if self.window:
            self.window.destroy()

def open_info_interface(content: str = "", save_fn=None):
    """Abre a interface WebView."""
    api = WebViewBridge(content, save_fn)
    
    # Localizar o arquivo HTML
    html_path = Path(__file__).resolve().parent / "fotonInfoInterface.html"
    
    # Se não existir no local de interfaces, tenta no assets
    if not html_path.exists():
        from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
        html_path = PathManager.get_app_dir() / "assets" / "fotonInfoInterface.html"

    # Fallback se ainda não existir
    if not html_path.exists():
        print(f"❌ Erro: Interface HTML não encontrada em {html_path}")
        return

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

if __name__ == "__main__":
    # Teste isolado
    example_md = "@nomeCliente; Fulano de Tal\n@valorProposta; [calculo: 1000*2]"
    open_info_interface(example_md)
