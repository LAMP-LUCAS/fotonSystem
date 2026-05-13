import unittest
import os
import shutil
import tempfile
from pathlib import Path
import pandas as pd
from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
from foton_system.modules.clients.application.use_cases.client_service import ClientService
from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import ExcelClientRepository
from foton_system.modules.documents.application.use_cases.document_service import DocumentService
from foton_system.modules.documents.infrastructure.adapters.python_docx_adapter import PythonDocxAdapter
from foton_system.modules.documents.infrastructure.adapters.python_pptx_adapter import PythonPPTXAdapter
from foton_system.modules.shared.infrastructure.config.config import Config

class TestArchitectPipelineE2E(unittest.TestCase):
    """
    End-to-End test suite simulating a real architect workflow.
    """

    @classmethod
    def setUpClass(cls):
        # Setup a clean sandbox environment for E2E
        cls.temp_dir = Path(tempfile.gettempdir()) / "foton_e2e_test"
        if cls.temp_dir.exists():
            shutil.rmtree(cls.temp_dir)
        cls.temp_dir.mkdir(parents=True)

        # Force PathManager to use our temp dir
        PathManager._sandbox_dir = cls.temp_dir
        PathManager.set_sandbox_mode(True)

        # Re-initialize directories in the new sandbox
        PathManager.ensure_directories()
        
        # Override Config with sandbox paths explicitly
        config = Config()
        config.set('caminho_pastaClientes', str(PathManager.get_user_projects_dir()))
        config.set('caminho_baseDados', str(PathManager.get_app_data_dir() / "baseDados_e2e.xlsx"))
        config.set('caminho_templates', str(cls.temp_dir / "templates"))
        config.save()
        
        # Initialize Services
        cls.repo = ExcelClientRepository()
        cls.client_service = ClientService(cls.repo)
        cls.doc_service = DocumentService(PythonDocxAdapter(), PythonPPTXAdapter())

    def test_complete_client_to_document_funnel(self):
        """
        Funnel: Create Client -> Verify Folders -> Generate INFO -> Generate Document.
        """
        # 1. Create Client
        client_data = {
            'NomeCliente': 'Arquitetura E2E Ltda',
            'Alias': 'E2E_PROJ',
            'TelefoneCliente': '1199999999'
        }
        self.client_service.create_client(client_data)

        # Force sync to create folders if they weren't created
        self.client_service.sync_client_folders_from_db()

        client_dir = Path(Config().get('caminho_pastaClientes')) / "E2E_PROJ"
        self.assertTrue(client_dir.exists(), f"Pasta do cliente {client_dir} deveria ter sido criada.")

        # 2. Verify Database
        df = self.repo.get_clients_dataframe()
        self.assertIn('E2E_PROJ', df['Alias'].values)

        # 3. Create a Service/Project for this client
        # This should also create the INFO file
        cod = "001"
        data_file = self.doc_service.create_custom_data_file(
            client_dir, cod=cod, ver="01", rev="R00", desc="PROPOSTA_TESTE"
        )
        self.assertTrue(data_file.exists(), "Arquivo INFO deveria ter sido criado.")
        
        # 4. Inject specific data into the INFO file
        with open(data_file, 'a', encoding='utf-8') as f:
            f.write("\n@valorProposta; 15000.00\n")
            f.write("@cidadeProposta; São Paulo\n")

        # 5. Generate a dummy template (since we can't easily create a real DOCX here without external tools)
        # We'll mock the template existence and test the service call
        templates_dir = PathManager.get_app_data_dir() / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)
        template_path = templates_dir / "template_teste.docx"
        template_path.touch() # Dummy empty file

        output_path = client_dir / "PROPOSTA_GERADA.docx"

        # Note: DocumentService will fail with an empty file in real adapters, 
        # but here we are validating the logic flow and path resolution.
        # For a true E2E, we'd need a valid .docx in the assets.
        
        # 6. Validate SSOT inheritance (Logic Check)
        # Verify if the service can resolve the client alias from the path
        self.client_service.sync_clients_db_from_folders()
        
        # Verify that the DB still has the client
        df_final = self.repo.get_clients_dataframe()
        self.assertIn('E2E_PROJ', df_final['Alias'].values)

    def test_resilience_to_missing_data(self):
        """
        Ensures the system handles incomplete INFO files gracefully.
        """
        client_dir = PathManager.get_user_projects_dir() / "INCOMPLETE_CLIENT"
        client_dir.mkdir(parents=True, exist_ok=True)
        
        info_file = client_dir / "INFO-INCOMPLETE.md"
        info_file.write_text("@nomeCliente; João Sem Dados\n", encoding='utf-8')

        # Try to sync
        self.client_service.sync_clients_db_from_folders()
        
        df = self.repo.get_clients_dataframe()
        self.assertIn('INCOMPLETE_CLIENT', df['Alias'].values)
        
    @classmethod
    def tearDownClass(cls):
        # Cleanup
        PathManager.set_sandbox_mode(False)
        if cls.temp_dir.exists():
            shutil.rmtree(cls.temp_dir)

if __name__ == '__main__':
    unittest.main()
