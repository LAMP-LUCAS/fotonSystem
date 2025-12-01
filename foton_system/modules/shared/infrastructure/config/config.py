import json
import os
from pathlib import Path

class Config:
    _instance = None
    _settings = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_settings()
        return cls._instance

    def _load_settings(self):
        # Assumes settings.json is in ../../../../../config/ relative to this file's parent
        # Current file: .../foton_system/modules/shared/infrastructure/config/config.py
        # Base dir (foton_system): .../
        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        config_path = base_dir / 'config' / 'settings.json'
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found at {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            self._settings = json.load(f)

    def get(self, key, default=None):
        return self._settings.get(key, default)

    @property
    def base_pasta_clientes(self):
        return Path(self.get('caminho_pastaClientes'))

    @property
    def base_dados(self):
        return Path(self.get('caminho_baseDados'))

    @property
    def base_clientes(self):
        return Path(self.get('caminho_baseClientes'))

    @property
    def base_servicos(self):
        return Path(self.get('caminho_baseServicos'))
    
    @property
    def templates_path(self):
        return Path(self.get('caminho_templates'))

    @property
    def ignored_folders(self):
        return self.get('ignored_folders', [])
