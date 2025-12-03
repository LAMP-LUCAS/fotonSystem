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
        from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService
        
        # Initialize environment (Self-Bootstrapping)
        # This ensures settings.json exists and points to valid files
        self._config_path = BootstrapService.initialize()

        # Load settings
        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                self._settings = json.load(f)
        except Exception as e:
            print(f"Error loading config from {self._config_path}: {e}")
            # If load fails, we might want to trigger a re-bootstrap or fail gracefully
            # For now, we just print the error.


    def set(self, key, value):
        """Updates a setting value in memory."""
        self._settings[key] = value

    def save(self):
        """Persists current settings to the JSON file."""
        # Ensure directory exists before saving
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_path, 'w', encoding='utf-8') as f:
            json.dump(self._settings, f, indent=4, ensure_ascii=False)

    def get(self, key, default=None):
        return self._settings.get(key, default)

    @property
    def workspace_path(self):
        """Returns the root directory of the current workspace (where settings.json is located)."""
        return self._config_path.parent

    @property
    def base_pasta_clientes(self):
        return Path(self.get('caminho_pastaClientes'))

    @property
    def base_dados(self):
        return Path(self.get('caminho_baseDados'))
    
    @property
    def templates_path(self):
        return Path(self.get('caminho_templates'))

    @property
    def ignored_folders(self):
        return self.get('ignored_folders', [])

    @property
    def clean_missing_variables(self):
        return self.get('clean_missing_variables', True)

    @property
    def missing_variable_placeholder(self):
        return self.get('missing_variable_placeholder', "---")

    @property
    def pomodoro_work_time(self):
        return self.get('pomodoro_work_time', 25)

    @property
    def pomodoro_short_break(self):
        return self.get('pomodoro_short_break', 5)

    @property
    def pomodoro_long_break(self):
        return self.get('pomodoro_long_break', 15)

    @property
    def pomodoro_cycles(self):
        return self.get('pomodoro_cycles', 4)
