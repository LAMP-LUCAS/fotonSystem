"""
Logger: Centralized logging configuration for FotonSystem.

Logs are written to both console and file (in AppData).
"""

import logging
import sys
from pathlib import Path

from foton_system.modules.shared.infrastructure.services.path_manager import PathManager


def setup_logger(name: str = "foton_system", level: int = logging.INFO) -> logging.Logger:
    """
    Sets up a logger that writes to a file and the console.
    
    Args:
        name: Logger name (default: "foton_system")
        level: Logging level (default: INFO)
    
    Returns:
        Configured Logger instance
    """
<<<<<<< HEAD
    # Se estiver rodando como executável (frozen), manda o log para o AppData para evitar Erro de Permissão
    if getattr(sys, 'frozen', False):
        import os
        from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService
        log_dir = BootstrapService.get_user_config_dir()
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file_path = log_dir / log_file
    else:
        log_file_path = Path(log_file)
=======
    # Always use AppData for log file to avoid permission issues
    log_dir = PathManager.get_app_data_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = PathManager.get_log_path()
>>>>>>> bd7b97aaa2f383cac97855c4cb7eca8ddf31252a

    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers multiple times if logger is already configured
    if logger.handlers:
        return logger

    # Console handler
    c_handler = logging.StreamHandler(sys.stdout)
<<<<<<< HEAD
    try:
        f_handler = logging.FileHandler(str(log_file_path), encoding='utf-8')
    except Exception as e:
        # Fallback para o console se o arquivo falhar
        print(f"Erro ao inicializar arquivo de log em {log_file_path}: {e}")
        f_handler = None

=======
>>>>>>> bd7b97aaa2f383cac97855c4cb7eca8ddf31252a
    c_handler.setLevel(level)
    c_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

<<<<<<< HEAD
    if f_handler:
        f_handler.setLevel(level)
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)
=======
    # File handler
    try:
        f_handler = logging.FileHandler(str(log_file_path), encoding='utf-8')
        f_handler.setLevel(level)
        f_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)
    except Exception as e:
        # Fallback: continue without file logging
        logger.warning(f"Could not initialize log file at {log_file_path}: {e}")
>>>>>>> bd7b97aaa2f383cac97855c4cb7eca8ddf31252a

    return logger
