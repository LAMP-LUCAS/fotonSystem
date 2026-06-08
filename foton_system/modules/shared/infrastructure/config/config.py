import json
import os
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

_SETTINGS_SCHEMA: Dict[str, type] = {
    "caminho_pastaClientes": str,
    "caminho_templates": str,
    "caminho_baseDados": str,
    "ignored_folders": list,
    "clean_missing_variables": bool,
    "missing_variable_placeholder": str,
    "folder_conventions": dict,
}


class Config:
    _instance: Optional["Config"] = None
    _settings: Dict[str, Any] = {}
    _config_path: Path

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_settings()
        return cls._instance

    def _validate_settings(self) -> None:
        """Validate types of critical settings, replacing invalid values with defaults."""
        for key, expected_type in _SETTINGS_SCHEMA.items():
            value = self._settings.get(key)
            if value is not None and not isinstance(value, expected_type):
                logging.getLogger("foton_config").warning(
                    "Config key '%s' has wrong type (expected %s, got %s). Using default.",
                    key, expected_type.__name__, type(value).__name__,
                )
                self._settings.pop(key, None)

    def _load_settings(self) -> None:
        from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService
        self._config_path = BootstrapService.initialize()

        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                self._settings = json.load(f)
        except Exception as e:
            print(f"Error loading config from {self._config_path}: {e}")

        self._validate_settings()

    def set(self, key: str, value: Any) -> None:
        """Updates a setting value in memory."""
        self._settings[key] = value

    def save(self) -> None:
        """Persists current settings to the JSON file."""
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_path, 'w', encoding='utf-8') as f:
            json.dump(self._settings, f, indent=4, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    @property
    def workspace_path(self) -> Path:
        """Returns the root directory of the current workspace (where settings.json is located)."""
        return self._config_path.parent

    @property
    def base_pasta_clientes(self) -> Path:
        return Path(self.get('caminho_pastaClientes'))

    @property
    def base_dados(self) -> Path:
        return Path(self.get('caminho_baseDados'))

    @property
    def templates_path(self) -> Path:
        return Path(self.get('caminho_templates'))

    @property
    def ignored_folders(self) -> List[str]:
        configured: List[str] = self.get('ignored_folders', [])
        functional: List[str] = [self.folder_doc, self.folder_adm, self.folder_op]
        deduped: List[str] = list(dict.fromkeys(configured + functional))
        return deduped

    @property
    def clean_missing_variables(self) -> bool:
        return bool(self.get('clean_missing_variables', True))

    @property
    def missing_variable_placeholder(self) -> str:
        return str(self.get('missing_variable_placeholder', "---"))

    @property
    def folder_doc(self) -> str:
        fc: Dict[str, Any] = self.get('folder_conventions', {})
        return str(fc.get('doc', '00_DOC'))

    @property
    def folder_adm(self) -> str:
        fc: Dict[str, Any] = self.get('folder_conventions', {})
        return str(fc.get('adm', '01_ADM'))

    @property
    def folder_op(self) -> str:
        fc: Dict[str, Any] = self.get('folder_conventions', {})
        return str(fc.get('op', '02_OPERACAO'))

    @property
    def folder_op_phases(self) -> List[str]:
        fc: Dict[str, Any] = self.get('folder_conventions', {})
        return list(fc.get('op_phases', ['EP', 'AP', 'EXE', 'REL']))

    @property
    def pomodoro_work_time(self) -> int:
        return int(self.get('pomodoro_work_time', 25))

    @property
    def pomodoro_short_break(self) -> int:
        return int(self.get('pomodoro_short_break', 5))

    @property
    def pomodoro_long_break(self) -> int:
        return int(self.get('pomodoro_long_break', 15))

    @property
    def pomodoro_cycles(self) -> int:
        return int(self.get('pomodoro_cycles', 4))

    @property
    def ui_mode(self) -> str:
        return str(self.get('ui_mode', 'auto'))

