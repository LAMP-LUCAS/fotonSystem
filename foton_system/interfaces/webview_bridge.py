"""
WebViewBridge - Ponte entre Python e Interface HTML (FotonInfoInterface).

Utiliza pywebview para abrir a interface de preenchimento de dados de forma nativa.
Permite ler arquivos MD do projeto e salvar o resultado diretamente no sistema.
"""

import json
import os
import sys
import webbrowser
from pathlib import Path
from typing import Optional

try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False

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
    """Abre a interface WebView ou fallback para Browser."""
    if not WEBVIEW_AVAILABLE:
        print("\n⚠️  Módulo 'webview' não disponível no ambiente atual.")
        print("💡 Tentando abrir a interface no seu navegador padrão...")
        _open_in_browser(content)
        return

    api = WebViewBridge(content, save_fn)
    
    # Localizar o arquivo HTML (sempre ao lado do .py em dev e frozen)
    html_path = Path(__file__).resolve().parent / "fotonInfoInterface.html"

    if not html_path.exists():
        print(f"❌ Erro: Interface HTML não encontrada. Tentando modo browser...")
        _open_in_browser(content)
        return

    try:
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
    except Exception as e:
        print(f"⚠️ Falha ao iniciar janela nativa: {e}")
        print("💡 Abrindo fallback no navegador...")
        _open_in_browser(content)

def _open_in_browser(content: str):
    """Fallback: Abre o HTML no navegador padrão."""
    html_path = Path(__file__).resolve().parent / "fotonInfoInterface.html"
    if html_path.exists():
        try:
            webbrowser.open(f"file:///{html_path.resolve()}")
            print("✅ Interface aberta no navegador.")
        except Exception as e:
            print(f"⚠️ Não foi possível abrir o navegador automaticamente: {e}")
            print(f"💡 Você pode abrir manualmente o arquivo: {html_path.resolve()}")
        
        print("📝 Nota: No modo navegador, você deve copiar o resultado final manualmente.")
    else:
        print("❌ Erro crítico: Arquivo HTML da interface não encontrado em lugar nenhum.")

if __name__ == "__main__":
    # Teste isolado
    example_md = "@nomeCliente; Fulano de Tal\n@valorProposta; [calculo: 1000*2]"
    open_info_interface(example_md)
