import os
import json
import shutil
from pathlib import Path
from platform import system

class BootstrapService:
    APP_NAME = "FotonSystem"
    
    @staticmethod
    def get_user_config_dir():
        """Retorna o caminho da pasta de configuração do usuário (Cross-Platform)."""
        home = Path.home()
        if system() == "Windows":
            return home / "AppData" / "Local" / BootstrapService.APP_NAME
        else:
            # Linux/Mac
            return home / f".{BootstrapService.APP_NAME.lower()}"

    @staticmethod
    def resolve_config_path():
        """
        Lógica de Cascata:
        1. Verifica pasta local (Modo Portátil).
        2. Verifica pasta do usuário (Modo Instalado).
        3. Retorna o caminho onde DEVERIA estar (preferência pelo usuário se não existir nenhum).
        """
        local_path = Path.cwd() / "settings.json"
        user_path = BootstrapService.get_user_config_dir() / "settings.json"

        # 1. Prioridade: Arquivo local existente (Override)
        if local_path.exists():
            return local_path
        
        # 2. Arquivo de usuário existente
        if user_path.exists():
            return user_path
            
        # 3. Default para criação: Pasta do Usuário (mais limpo)
        # Mas se estiver rodando como script (dev), pode ser melhor local.
        # Vamos padronizar: Se for EXE congelado -> User Path. Se for Script -> Local.
        import sys
        if getattr(sys, 'frozen', False):
            return user_path
        else:
            return local_path

    @staticmethod
    def initialize():
        """Garante que o settings.json exista no local correto."""
        config_path = BootstrapService.resolve_config_path()
        config_dir = config_path.parent
        
        # Garante que a pasta existe
        config_dir.mkdir(parents=True, exist_ok=True)

        if not config_path.exists():
            print(f"⚙️ Criando configuração padrão em: {config_path}")
            BootstrapService._create_default_settings(config_path)
        
        return config_path

    @staticmethod
    def _create_default_settings(path):
        # Tenta copiar do template interno se estiver empacotado
        # Caminho base do recurso (seja dev ou freeze)
        import sys
        if getattr(sys, 'frozen', False):
            base_dir = Path(sys._MEIPASS)
        else:
            base_dir = Path(__file__).resolve().parents[4] # Adjust based on depth
            
        template_source = base_dir / "foton_system" / "config" / "settings.json.example"
        
        default_settings = {
            "caminho_pastaClientes": str(Path.home() / "Documents" / "FotonProjects"),
            "caminho_templates": str(Path.home() / "Documents" / "FotonTemplates"),
            "caminho_baseDados": str(Path.home() / "Documents" / "FotonSystem" / "baseDados.xlsx"),
            "ignored_folders": ["DOC", "ARQ", "HID", "ELE", "STR", "PL", "EVT"],
            "clean_missing_variables": True,
            "missing_variable_placeholder": "---",
            "enable_mcp": True
        }

        try:
            # Tenta carregar do example se existir
            if template_source.exists():
                with open(template_source, 'r', encoding='utf-8') as f:
                    default_settings.update(json.load(f))
        except:
            pass

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, indent=4)
