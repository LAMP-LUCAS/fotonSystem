"""
SandboxService: Manages the volatile testing environment.
"""

import json
import shutil
from pathlib import Path
from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
from foton_system.modules.shared.infrastructure.config.logger import setup_logger

logger = setup_logger()

class SandboxService:
    """
    Handles initialization, seeding, and teardown of the Sandbox mode.
    """

    @staticmethod
    def initialize_sandbox():
        """
        Activates sandbox mode and prepares the environment.
        """
        logger.info("Initializing Sandbox Mode...")
        PathManager.set_sandbox_mode(True)
        
        # Ensure base directories exist in the sandbox
        app_data_dir = PathManager.get_app_data_dir()
        projects_dir = PathManager.get_user_projects_dir()
        
        app_data_dir.mkdir(parents=True, exist_ok=True)
        projects_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a sandbox-specific settings.json
        SandboxService._create_sandbox_settings()
        
        # Seed with dummy data
        SandboxService._seed_sandbox()
        
        logger.info(f"Sandbox initialized at {PathManager.get_sandbox_dir()}")

    @staticmethod
    def _create_sandbox_settings():
        """Creates a minimal settings.json for the sandbox."""
        settings_path = PathManager.get_settings_path()
        templates_dir = PathManager.get_sandbox_dir() / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        settings = {
            "caminho_pastaClientes": str(PathManager.get_user_projects_dir()),
            "caminho_templates": str(templates_dir),
            "caminho_baseDados": str(PathManager.get_app_data_dir() / "baseDados_sandbox.xlsx"),
            "ignored_folders": ["DOC", "ARQ", "HID", "ELE", "STR", "PL", "EVT"],
            "clean_missing_variables": True,
            "missing_variable_placeholder": "[SANDBOX-MISSING]",
            "enable_mcp": True
        }
        
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)

    @staticmethod
    def _seed_sandbox():
        """Populates the sandbox with example data."""
        # 1. Create a dummy client
        projects_dir = PathManager.get_user_projects_dir()
        client_dir = projects_dir / "CLIENTE_EXEMPLO"
        client_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Create standard folder structure for dummy client
        (client_dir / "01_ADMINISTRATIVO").mkdir(exist_ok=True)
        (client_dir / "02_FINANCEIRO").mkdir(exist_ok=True)
        (client_dir / "03_PROJETOS").mkdir(exist_ok=True)
        
        # 3. Create a dummy INFO file
        info_file = client_dir / "INFO-CLIENTE_EXEMPLO.md"
        content = """# DADOS DO CLIENTE (MODO SANDBOX)
@Nome; Cliente de Teste Sandbox
@Email; teste@sandbox.com
@Cidade; Cidade Virtual
@DataAtual; 01 de Janeiro de 2026
"""
        info_file.write_text(content, encoding='utf-8')
        
        # 4. Create a dummy finance ledger
        finance_file = client_dir / "FINANCEIRO.csv"
        finance_file.write_text("Data,Descricao,Valor,Tipo\n2026-01-01,Saldo Inicial Sandbox,1000.00,ENTRADA", encoding='utf-8')
        
        # 5. Create a dummy template in the sandbox templates dir
        templates_dir = PathManager.get_sandbox_dir() / "templates"
        dummy_template = templates_dir / "01-MOD_DOC_PROPOSTA_V00_R00_TESTE.docx"
        dummy_template.touch() # Just an empty file for listing tests
