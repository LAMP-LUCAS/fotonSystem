"""
PathManager: Centralized path resolution for FotonSystem.

This module provides a single source of truth for all system paths,
ensuring consistency across development, frozen (EXE), and installed modes.
"""

import sys
from pathlib import Path
from platform import system


class PathManager:
    """
    Manages all system paths for FotonSystem.
    
    Paths are organized into three categories:
    - App Data: Configuration files, logs, and system databases
    - Install Dir: The application binaries and assets
    - User Projects: User-facing project files
    """
    
    APP_NAME = "FotonSystem"
    _sandbox_mode = False
    _sandbox_dir = None

    @classmethod
    def set_sandbox_mode(cls, enabled: bool):
        """Activates or deactivates sandbox mode."""
        cls._sandbox_mode = enabled
        if enabled and cls._sandbox_dir is None:
            import tempfile
            temp_dir = Path(tempfile.gettempdir())
            cls._sandbox_dir = temp_dir / "foton_sandbox"
            cls._sandbox_dir.mkdir(parents=True, exist_ok=True)
        elif not enabled:
            cls._sandbox_dir = None

    @classmethod
    def get_sandbox_dir(cls) -> Path:
        """Returns the temporary sandbox directory."""
        if cls._sandbox_dir is None:
            import tempfile
            temp_dir = Path(tempfile.gettempdir())
            return temp_dir / "foton_sandbox"
        return cls._sandbox_dir

    @classmethod
    def is_sandbox_active(cls) -> bool:
        """Checks if sandbox mode is active."""
        return cls._sandbox_mode
    
    # --- Core Path Getters ---
    
    @staticmethod
    def get_app_data_dir() -> Path:
        """
        Returns the application data directory.
        
        Windows: %LOCALAPPDATA%/FotonSystem
        Linux/Mac: ~/.fotonsystem
        """
        if PathManager.is_sandbox_active():
            return PathManager.get_sandbox_dir() / "appdata"

        home = Path.home()
        if system() == "Windows":
            return home / "AppData" / "Local" / PathManager.APP_NAME
        else:
            return home / f".{PathManager.APP_NAME.lower()}"
    
    @staticmethod
    def get_install_dir() -> Path:
        """
        Returns the installation directory.
        
        - In frozen (EXE) mode: The directory containing the EXE
        - In dev mode: The project root
        
        Windows Installer Target: %LOCALAPPDATA%/Programs/FotonSystem
        """
        if getattr(sys, 'frozen', False):
            # In PyInstaller onedir mode, the EXE is in the root of the bundle
            return Path(sys.executable).parent
        else:
            # Dev mode: find project root
            return PathManager._find_project_root()
    
    @staticmethod
    def get_assets_dir() -> Path:
        """
        Returns the assets directory.
        
        - In frozen mode: Uses _MEIPASS (PyInstaller's temp extraction folder)
        - In dev mode: Uses the project's foton_system/assets folder
        """
        if getattr(sys, 'frozen', False):
            return Path(sys._MEIPASS) / "foton_system" / "assets"
        else:
            return PathManager._find_project_root() / "foton_system" / "assets"
    
    @staticmethod
    def get_resources_dir() -> Path:
        """Returns the resources directory (templates, skeletons, etc)."""
        if getattr(sys, 'frozen', False):
            return Path(sys._MEIPASS) / "foton_system" / "resources"
        else:
            return PathManager._find_project_root() / "foton_system" / "resources"
    
    @staticmethod
    def get_config_dir() -> Path:
        """Returns the config directory (bundled config files)."""
        if getattr(sys, 'frozen', False):
            return Path(sys._MEIPASS) / "foton_system" / "config"
        else:
            return PathManager._find_project_root() / "foton_system" / "config"
    
    @staticmethod
    def get_user_projects_dir() -> Path:
        """
        Returns the default user projects directory.
        
        Windows: Documents/FotonProjects
        Linux/Mac: ~/FotonProjects
        """
        if PathManager.is_sandbox_active():
            return PathManager.get_sandbox_dir() / "projects"

        if system() == "Windows":
            return Path.home() / "Documents" / "FotonProjects"
        else:
            return Path.home() / "FotonProjects"
    
    # --- Specific File Paths ---
    
    @staticmethod
    def get_settings_path() -> Path:
        """Returns the path to settings.json."""
        return PathManager.get_app_data_dir() / "settings.json"
    
    @staticmethod
    def get_log_path() -> Path:
        """Returns the path to the log file."""
        return PathManager.get_app_data_dir() / "foton_system.log"
    
    # --- Helper Methods ---
    
    @staticmethod
    def _find_project_root() -> Path:
        """
        Finds the project root by searching upwards for markers.
        
        Markers: .git folder or foton_system folder
        """
        current_path = Path(__file__).resolve()
        
        # Search upwards
        for parent in current_path.parents:
            if (parent / ".git").exists() or (parent / "foton_system").is_dir():
                return parent
        
        # Fallback: current working directory
        return Path.cwd()
    
    @staticmethod
    def ensure_directories():
        """
        Creates all required directories if they don't exist.
        
        Call this at application startup.
        """
        dirs_to_create = [
            PathManager.get_app_data_dir(),
            PathManager.get_user_projects_dir(),
        ]
        
        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def is_frozen() -> bool:
        """Returns True if running as a frozen (PyInstaller) executable."""
        return getattr(sys, 'frozen', False)
    
    @staticmethod
    def get_version() -> str:
        """Returns the application version."""
        try:
            from foton_system import __version__
            return __version__
        except ImportError:
            return "0.0.0"
