import PyInstaller.__main__
import os
from pathlib import Path

# Configuração de Caminhos
BASE_DIR = Path(__file__).resolve().parent
FOTON_SYSTEM_DIR = BASE_DIR / 'foton_system'
ICON_PATH = FOTON_SYSTEM_DIR / 'assets' / 'foton.ico'
ENTRY_POINT = FOTON_SYSTEM_DIR / 'interfaces' / 'cli' / 'main.py'

def build():
    print("🚀 Iniciando Build do Foton System (EXE)...")
    
    # Argumentos do PyInstaller
    args = [
        str(ENTRY_POINT),                       # Entry Point Absoluto
        '--name=FotonSystem',                   # Nome do Executável
        '--onefile',                            # Arquivo Único (Mais fácil distribuição)
        '--clean',                              # Limpar cache
        '--noconfirm',                          # Não perguntar confirmação
        f'--icon={str(ICON_PATH)}',             # Ícone
        
        # --- Importação de Dados (Assets, Templates, Skeletons) ---
        f'--add-data={FOTON_SYSTEM_DIR}/assets;foton_system/assets',
        f'--add-data={FOTON_SYSTEM_DIR}/resources;foton_system/resources',
        f'--add-data={FOTON_SYSTEM_DIR}/config;foton_system/config',
        # Incluir scripts auxiliares se quisermos rodar GUI separadamente, 
        # mas como é onefile, eles ficam embutidos. 
        
        # --- Imports Ocultos ---
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--hidden-import=docx',
        '--hidden-import=pptx',
        '--hidden-import=mcp',
        '--hidden-import=foton_system.modules.finance',
        '--hidden-import=foton_system.modules.sync',
        '--hidden-import=tkinter', # GUI
        '--hidden-import=winshell',
        '--hidden-import=win32com',
        '--hidden-import=pythoncom',
        
        # --- Caminhos de Busca ---
        f'--paths={BASE_DIR}',
    ]

    # Executar
    try:
        PyInstaller.__main__.run(args)
        print("\n✅ Build Concluído!")
        print(f"O executável está em: {BASE_DIR / 'dist' / 'FotonSystem.exe'}")
    except Exception as e:
        print(f"❌ Erro no build: {e}")

if __name__ == "__main__":
    build()
