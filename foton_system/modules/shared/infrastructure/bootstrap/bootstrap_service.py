import os
import sys
import shutil
import json
from pathlib import Path
from colorama import Fore, Style

class BootstrapService:
    """
    Responsible for initializing the user's environment (Self-Bootstrapping).
    Ensures that configuration, databases, and templates exist.
    """
    
    APP_NAME = "FotonSystem"
    
    @classmethod
    def initialize(cls):
        """
        Main entry point for bootstrapping.
        Returns the path to the valid settings.json.
        """
        # Strategy:
        # 1. Check for settings.json in Documents/FotonSystem (Primary Workspace)
        # 2. Check for settings.json in AppData (Legacy/Fallback)
        # 3. If neither, install Skeleton to Documents/FotonSystem
        
        docs_dir = Path(os.path.expanduser("~/Documents")) / cls.APP_NAME
        app_data_dir = Path(os.getenv('APPDATA')) / cls.APP_NAME
        
        workspace_settings = docs_dir / 'settings.json'
        appdata_settings = app_data_dir / 'settings.json'
        
        # 1. Check Workspace (Preferred)
        if workspace_settings.exists() and cls._validate_paths(workspace_settings):
            return workspace_settings
            
        # 2. Check AppData (Legacy)
        if appdata_settings.exists() and cls._validate_paths(appdata_settings):
            return appdata_settings
            
        # 3. Bootstrap (Install to Workspace)
        print(Fore.CYAN + "⚠️  Ambiente não detectado.")
        print(Fore.CYAN + f"🚀 Criando Workspace Portátil em: {docs_dir}")
        cls._install_skeleton(docs_dir, workspace_settings)
        
        return workspace_settings

    @classmethod
    def _validate_paths(cls, settings_path):
        """
        Checks if the paths in settings.json actually exist.
        """
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            # Check key paths
            paths_to_check = [
                settings.get('caminho_baseDados'),
                settings.get('caminho_templates')
            ]
            
            for p in paths_to_check:
                if not p or not Path(p).exists():
                    return False
            return True
        except Exception:
            return False

    @classmethod
    def _install_skeleton(cls, target_dir, settings_path):
        """
        Deploys the skeleton files to the target directory
        and creates a new settings.json there.
        """
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Source of Skeleton (inside the exe or source code)
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
            skeleton_source = base_path / 'foton_system' / 'resources' / 'skeleton'
        else:
            base_path = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
            skeleton_source = base_path / 'foton_system' / 'resources' / 'skeleton'
            
        if not skeleton_source.exists():
            print(Fore.RED + f"❌ Erro Crítico: Kit Inicial não encontrado em {skeleton_source}")
            return

        # Copy Files
        print(Fore.YELLOW + "📂 Copiando arquivos do sistema...")
        
        # Copy Excel files
        for item in skeleton_source.iterdir():
            if item.is_file():
                target = target_dir / item.name
                if not target.exists():
                    shutil.copy2(item, target)
                    print(f"   - Criado: {item.name}")
            elif item.is_dir():
                target = target_dir / item.name
                if not target.exists():
                    shutil.copytree(item, target)
                    print(f"   - Criado pasta: {item.name}")

        # Create settings.json pointing to this new location
        # Use absolute paths for robustness
        settings = {
            "caminho_pastaClientes": str(target_dir / "CLIENTES"),
            "caminho_baseDados": str(target_dir / "baseDados.xlsx"),
            "caminho_baseClientes": str(target_dir / "baseClientes.xlsx"),
            "caminho_baseServicos": str(target_dir / "baseServicos.xlsx"),
            "caminho_templates": str(target_dir / "KIT_DOC"),
            "ignored_folders": ["DOC", "ARQ", "HID", "ELE", "STR", "PL", "EVT"],
            "clean_missing_variables": True,
            "missing_variable_placeholder": "---",
             # Pomodoro defaults
            "pomodoro_work_time": 25,
            "pomodoro_short_break": 5,
            "pomodoro_long_break": 15,
            "pomodoro_cycles": 4
        }
        
        # Create CLIENTES folder
        (target_dir / "CLIENTES").mkdir(exist_ok=True)
        
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
            
        print(Fore.GREEN + "✅ Workspace configurado com sucesso!")
