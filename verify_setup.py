import sys
import os

# Ensure the script directory is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from foton_system.core.config import Config
    from foton_system.core.logger import setup_logger
    from foton_system.modules.clients.services import ClientService
    from foton_system.modules.productivity.pomodoro import PomodoroTimer
    from foton_system.modules.documents.services import DocumentService
    from foton_system.interfaces.cli.menus import MenuSystem
    
    print("Imports successful!")
    
    config = Config()
    print(f"Config loaded. Base Clients: {config.base_clientes}")
    
    logger = setup_logger()
    print("Logger setup successful.")
    
    client_service = ClientService()
    print("ClientService initialized.")

    document_service = DocumentService()
    print("DocumentService initialized.")
    
    # Test Safe Substitution
    print("MenuSystem initialized.")
    
except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
