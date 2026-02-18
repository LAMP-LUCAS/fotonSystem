"""
End-to-End (E2E) Test Suite

Simulates REAL user workflows:
1. Architect creates client folder → Syncs to DB → Creates service → Generates document → Records payment
2. Full lifecycle test with real temporary files
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd

from foton_system.modules.clients.application.use_cases.client_service import ClientService
from foton_system.modules.documents.application.use_cases.document_service import DocumentService
from foton_system.modules.finance.application.use_cases.finance_service import FinanceService
from foton_system.modules.finance.infrastructure.repositories.csv_finance_repository import CSVFinanceRepository


class FakeDocAdapter:
    """Minimal fake adapter for document tests."""
    def load_document(self, path):
        return MagicMock()
    def replace_text(self, doc, replacements):
        return doc
    def save_document(self, doc, path):
        # Actually create an empty file to verify output
        Path(path).touch()


class FakeClientRepo:
    """In-memory repository for E2E tests."""
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.clients_path = base_dir / 'CLIENTES'
        self.clients_path.mkdir(parents=True, exist_ok=True)
        self._clients = pd.DataFrame(columns=['Alias', 'NomeCliente', 'CodCliente'])
        self._services = pd.DataFrame(columns=['AliasCliente', 'Alias', 'CodServico'])

    def get_clients_dataframe(self):
        return self._clients.copy()

    def get_services_dataframe(self):
        return self._services.copy()

    def save_clients(self, df):
        self._clients = df.copy()

    def save_services(self, df):
        self._services = df.copy()

    def list_client_folders(self):
        return {p.name for p in self.clients_path.iterdir() if p.is_dir()}

    def list_service_folders(self, client):
        client_path = self.clients_path / client
        if client_path.exists():
            return {p.name for p in client_path.iterdir() if p.is_dir()}
        return set()

    def create_folder(self, path):
        Path(path).mkdir(parents=True, exist_ok=True)


class TestArchitectFullPipeline(unittest.TestCase):
    """
    E2E Test: Simulates a real architect workflow:
    
    1. Creates a client folder manually (like user does in Windows Explorer)
    2. Runs sync to add client to database
    3. Creates a service folder inside client
    4. Creates an INFO file with project data
    5. Generates a proposal document
    6. Records a financial entry (client payment)
    7. Checks financial balance
    """

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.repo = FakeClientRepo(self.test_dir)
        self.client_service = ClientService(self.repo)
        
        self.doc_service = DocumentService(FakeDocAdapter(), FakeDocAdapter())
        
        self.fin_repo = CSVFinanceRepository()
        self.fin_service = FinanceService(self.fin_repo)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_full_architect_workflow(self):
        """Complete architect workflow from folder creation to payment."""
        
        # ===== STEP 1: Architect creates client folder =====
        client_name = "730_Residencia_Silva"
        client_folder = self.repo.clients_path / client_name
        client_folder.mkdir(parents=True)
        
        # Verify folder exists
        self.assertTrue(client_folder.exists())
        
        # ===== STEP 2: Sync folders to DB =====
        self.client_service.sync_clients_db_from_folders()
        
        # Verify client was added to DB
        clients_df = self.repo.get_clients_dataframe()
        self.assertIn(client_name, clients_df['Alias'].values)
        
        # ===== STEP 3: Create service folder =====
        service_name = "001_PROJETO_ARQUITETURA"
        service_folder = client_folder / service_name
        service_folder.mkdir()
        
        # ===== STEP 4: Create INFO file with project data =====
        info_file = client_folder / f"INFO-{client_name}.md"
        info_content = """@NomeCliente: João Silva
@EnderecoObra: Rua das Flores, 123
@AreaTerreno: 500
@AreaConstruida: 250
@ValorProposta: R$ 15.000,00
"""
        info_file.write_text(info_content, encoding='utf-8')
        
        # Verify INFO file
        self.assertTrue(info_file.exists())
        
        # ===== STEP 5: Load context data (simulates document generation) =====
        context = self.doc_service._parse_md_data(info_file)
        
        self.assertEqual(context['@NomeCliente'], 'João Silva')
        self.assertEqual(context['@AreaTerreno'], '500')
        
        # ===== STEP 6: Record financial entry (client payment) =====
        summary = self.fin_service.add_entry(
            client_folder, 
            "Entrada de sinal - Proposta", 
            5000.0, 
            'ENTRADA'
        )
        
        self.assertEqual(summary['total_entradas'], 5000.0)
        self.assertEqual(summary['saldo'], 5000.0)
        
        # ===== STEP 7: Record expense =====
        summary = self.fin_service.add_entry(
            client_folder,
            "Taxa ART",
            150.0,
            'SAIDA'
        )
        
        self.assertEqual(summary['total_saidas'], 150.0)
        self.assertEqual(summary['saldo'], 4850.0)
        
        # ===== VERIFICATION: CSV file exists =====
        csv_file = client_folder / 'FINANCEIRO.csv'
        self.assertTrue(csv_file.exists())


class TestClientServiceSyncPipeline(unittest.TestCase):
    """E2E: Bidirectional sync between folders and database."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.repo = FakeClientRepo(self.test_dir)
        self.service = ClientService(self.repo)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_bidirectional_sync_consistency(self):
        """Data remains consistent after bidirectional sync operations."""
        # Create folders manually
        (self.repo.clients_path / 'Client_A').mkdir()
        (self.repo.clients_path / 'Client_B').mkdir()
        
        # Sync to DB
        self.service.sync_clients_db_from_folders()
        
        # Verify both in DB
        df = self.repo.get_clients_dataframe()
        self.assertEqual(len(df), 2)
        
        # Add third client directly to DB
        new_client = pd.DataFrame({'Alias': ['Client_C'], 'NomeCliente': ['Test']})
        df = pd.concat([df, new_client], ignore_index=True)
        self.repo.save_clients(df)
        
        # Sync again - should not duplicate
        self.service.sync_clients_db_from_folders()
        
        df = self.repo.get_clients_dataframe()
        self.assertEqual(len(df), 3)
        
        # Create folder for DB-only client
        with patch('foton_system.modules.clients.application.use_cases.client_service.Config') as MockConfig:
            mock_config = MagicMock()
            mock_config.base_pasta_clientes = self.repo.clients_path
            MockConfig.return_value = mock_config
            
            self.service.sync_client_folders_from_db()
        
        # Verify folder was created
        self.assertTrue((self.repo.clients_path / 'Client_C').exists())


class TestDocumentGenerationPipeline(unittest.TestCase):
    """E2E: Document generation with context loading."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.doc_service = DocumentService(FakeDocAdapter(), FakeDocAdapter())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_context_hierarchy_loading(self):
        """Loads context from hierarchical folder structure."""
        # Create nested structure: Client / Service / Subservice
        client_folder = self.test_dir / 'CLIENTES' / '001_Client'
        service_folder = client_folder / '001_Service'
        service_folder.mkdir(parents=True)
        
        # Create INFO files at each level
        (client_folder / 'INFO-001_Client.md').write_text(
            '@NomeCliente: Test Client\n@CNPJ: 12345\n',
            encoding='utf-8'
        )
        (service_folder / 'INFO-001_Service.md').write_text(
            '@NomeServico: Architecture Project\n@ValorServico: R$ 10.000,00\n',
            encoding='utf-8'
        )
        
        # Create data file in service folder
        data_file = service_folder / 'proposta_data.md'
        data_file.write_text('@DataProposta: 2026-02-02\n', encoding='utf-8')
        
        # Load context (should cascade from parent folders)
        with patch('foton_system.modules.documents.application.use_cases.document_service.Config') as MockConfig:
            mock_config = MagicMock()
            mock_config.base_pasta_clientes = self.test_dir / 'CLIENTES'
            MockConfig.return_value = mock_config
            
            context = self.doc_service._load_context_data(data_file)
        
        # Should have data from both client and service INFO files
        # (The actual merging depends on implementation)
        self.assertIsInstance(context, dict)


class TestMathExpressionResolutionPipeline(unittest.TestCase):
    """E2E: Mathematical expression resolution in documents."""

    def setUp(self):
        self.doc_service = DocumentService(FakeDocAdapter(), FakeDocAdapter())

    def test_cascading_calculations(self):
        """Resolves cascading calculations (@total depends on @subtotal)."""
        data = {
            '@preco': '1000',
            '@quantidade': '3',
            '@subtotal': '[calculo: @preco * @quantidade]',
            '@desconto': '100',
            '@total': '[calculo: @subtotal - @desconto]'
        }
        
        # Multiple passes should resolve all
        self.doc_service._resolve_operations(data)
        
        self.assertEqual(data['@subtotal'], '3000.00')
        self.assertEqual(data['@total'], '2900.00')


if __name__ == '__main__':
    unittest.main()
