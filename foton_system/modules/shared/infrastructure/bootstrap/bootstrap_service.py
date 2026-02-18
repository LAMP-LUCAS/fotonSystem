"""
BootstrapService: Initializes the FotonSystem environment.

This service ensures that the application has a valid configuration file
and all necessary directories before starting.
"""

import json
from pathlib import Path

from foton_system.modules.shared.infrastructure.services.path_manager import PathManager


class BootstrapService:
    """
    Handles first-run setup and configuration initialization.
    
    Uses PathManager for all path resolution to ensure consistency.
    """
    
    APP_NAME = PathManager.APP_NAME
    
    @staticmethod
    def get_user_config_dir() -> Path:
        """Returns the user config directory (delegates to PathManager)."""
        return PathManager.get_app_data_dir()

    @staticmethod
    def resolve_config_path() -> Path:
        """
        Resolves the path to settings.json with cascade logic:
        
        1. Local folder (portable mode override)
        2. AppData folder (standard installed mode)
        3. Default to AppData for creation
        """
        local_path = Path.cwd() / "settings.json"
        user_path = PathManager.get_settings_path()

        # 1. Priority: Existing local file (portable override)
        if local_path.exists():
            return local_path
        
        # 2. Existing user file
        if user_path.exists():
            return user_path
            
        # 3. Default for creation: AppData in frozen mode, local in dev mode
        if PathManager.is_frozen():
            return user_path
        else:
            return local_path

    @staticmethod
    def initialize() -> Path:
        """
        Ensures the application environment is ready.
        
        Creates:
        - AppData directory
        - settings.json with defaults (if missing)
        
        Returns:
            Path to the active settings.json
        """
        # Ensure all required directories exist
        PathManager.ensure_directories()
        
        config_path = BootstrapService.resolve_config_path()
        config_dir = config_path.parent
        
        # Ensure config directory exists
        config_dir.mkdir(parents=True, exist_ok=True)

        if not config_path.exists():
            print(f"⚙️ Criando configuração padrão em: {config_path}")
            BootstrapService._create_default_settings(config_path)
        
        return config_path

    @staticmethod
    def _create_default_settings(path: Path):
        """Creates a default settings.json file."""
        
        # Try to load from bundled template
        template_source = PathManager.get_config_dir() / "settings.json.example"
        
        default_settings = {
            "caminho_pastaClientes": str(PathManager.get_user_projects_dir()),
            "caminho_templates": str(Path.home() / "Documents" / "FotonTemplates"),
            "caminho_baseDados": str(PathManager.get_app_data_dir() / "baseDados.xlsx"),
            "ignored_folders": ["DOC", "ARQ", "HID", "ELE", "STR", "PL", "EVT"],
            "clean_missing_variables": True,
            "missing_variable_placeholder": "---",
            "enable_mcp": True
        }

        try:
            # Try to load from example if it exists
            if template_source.exists():
                with open(template_source, 'r', encoding='utf-8') as f:
                    default_settings.update(json.load(f))
        except Exception:
            pass

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, indent=4, ensure_ascii=False)
    
    @staticmethod
    def is_first_run() -> bool:
        """Returns True if this is the first time the app is running."""
        return not PathManager.get_settings_path().exists()
