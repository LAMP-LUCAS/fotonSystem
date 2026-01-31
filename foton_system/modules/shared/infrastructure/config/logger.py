import logging
import sys
from pathlib import Path

def setup_logger(name="foton_system", log_file="foton_system.log", level=logging.INFO):
    """
    Sets up a logger that writes to a file and the console.
    """
    # Se estiver rodando como executável (frozen), manda o log para o AppData para evitar Erro de Permissão
    if getattr(sys, 'frozen', False):
        import os
        from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService
        log_dir = BootstrapService.get_user_config_dir()
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file_path = log_dir / log_file
    else:
        log_file_path = Path(log_file)

    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers multiple times if logger is already configured
    if logger.handlers:
        return logger

    # Create handlers
    c_handler = logging.StreamHandler(sys.stdout)
    try:
        f_handler = logging.FileHandler(str(log_file_path), encoding='utf-8')
    except Exception as e:
        # Fallback para o console se o arquivo falhar
        print(f"Erro ao inicializar arquivo de log em {log_file_path}: {e}")
        f_handler = None

    c_handler.setLevel(level)
    f_handler.setLevel(level)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    f_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

    if f_handler:
        f_handler.setLevel(level)
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)

    return logger
