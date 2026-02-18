"""
Real-World Integration Tests

Uses actual temporary Excel files and folder structures instead of mocks.
Tests the full sync cycle from folder creation to Excel updates.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import pandas as pd

from foton_system.modules.clients.application.use_cases.client_service import ClientService
from foton_system.modules.clients.application.ports.client_repository_port import ClientRepositoryPort


class TempFileClientRepository(ClientRepositoryPort):
    """
    Real-file based repository that uses temporary directories.
    
    This is a test double that operates on actual files, not mocks.
    It reuses the same interface as production but with isolated temp paths.
    """
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.db_path = base_dir / 'baseDados.xlsx'
        self.clients_path = base_dir / 'CLIENTES'
        self.clients_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize Excel with empty sheets
        with pd.ExcelWriter(self.db_path, engine='openpyxl') as writer:
            pd.DataFrame(columns=['Alias', 'NomeCliente', 'CodCliente']).to_excel(
                writer, sheet_name='baseClientes', index=False
            )
            pd.DataFrame(columns=['AliasCliente', 'Alias', 'CodServico']).to_excel(
                writer, sheet_name='baseServicos', index=False
            )

    def get_clients_dataframe(self) -> pd.DataFrame:
        return pd.read_excel(self.db_path, sheet_name='baseClientes')

    def get_services_dataframe(self) -> pd.DataFrame:
        return pd.read_excel(self.db_path, sheet_name='baseServicos')

    def save_clients(self, df: pd.DataFrame):
        with pd.ExcelWriter(self.db_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name='baseClientes', index=False)

    def save_services(self, df: pd.DataFrame):
        with pd.ExcelWriter(self.db_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name='baseServicos', index=False)

    def list_client_folders(self) -> set:
        return {p.name for p in self.clients_path.iterdir() if p.is_dir()}

    def list_service_folders(self, client_name: str) -> set:
        client_path = self.clients_path / client_name
        if client_path.exists():
            return {p.name for p in client_path.iterdir() if p.is_dir()}
        return set()

    def create_folder(self, path):
        Path(path).mkdir(parents=True, exist_ok=True)


class TestFullSyncCycle(unittest.TestCase):
    """Tests the full bidirectional sync cycle with real files."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.repo = TempFileClientRepository(self.test_dir)
        self.service = ClientService(self.repo)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_folder_to_db_sync(self):
        """Creating a folder should add client to Excel after sync."""
        # Create folder manually
        (self.repo.clients_path / 'NewClient').mkdir()
        
        # Run sync
        self.service.sync_clients_db_from_folders()
        
        # Verify Excel updated
        df = self.repo.get_clients_dataframe()
        self.assertIn('NewClient', df['Alias'].values)

    def test_db_to_folder_sync(self):
        """Adding client to Excel should create folder after sync."""
        # Add to DB
        df = pd.DataFrame({'Alias': ['DBClient'], 'NomeCliente': ['Test Client']})
        self.repo.save_clients(df)
        
        # Patch Config to use our temp path
        from unittest.mock import patch, MagicMock
        with patch('foton_system.modules.clients.application.use_cases.client_service.Config') as MockConfig:
            mock_config = MagicMock()
            mock_config.base_pasta_clientes = self.repo.clients_path
            MockConfig.return_value = mock_config
            
            self.service.sync_client_folders_from_db()
        
        # Verify folder exists
        self.assertTrue((self.repo.clients_path / 'DBClient').exists())

    def test_full_roundtrip_consistency(self):
        """Data should remain consistent after multiple sync cycles."""
        # Step 1: Create folders
        (self.repo.clients_path / 'Client1').mkdir()
        (self.repo.clients_path / 'Client2').mkdir()
        
        # Step 2: Sync to DB
        self.service.sync_clients_db_from_folders()
        
        # Step 3: Add more clients to DB
        df = self.repo.get_clients_dataframe()
        new_row = pd.DataFrame({'Alias': ['Client3']})
        df = pd.concat([df, new_row], ignore_index=True)
        self.repo.save_clients(df)
        
        # Step 4: Sync back (should not duplicate)
        self.service.sync_clients_db_from_folders()
        
        # Verify: 3 unique clients
        final_df = self.repo.get_clients_dataframe()
        self.assertEqual(len(final_df['Alias'].dropna().unique()), 3)


class TestServiceSync(unittest.TestCase):
    """Tests for service folder synchronization."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.repo = TempFileClientRepository(self.test_dir)
        self.service = ClientService(self.repo)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_service_folders_detected(self):
        """Service folders inside client folders should be detected."""
        # Create structure: CLIENTES/Client1/Service1
        client_folder = self.repo.clients_path / 'Client1'
        client_folder.mkdir()
        (client_folder / 'Service1').mkdir()
        (client_folder / 'Service2').mkdir()
        
        # Verify detection
        services = self.repo.list_service_folders('Client1')
        self.assertEqual(services, {'Service1', 'Service2'})


if __name__ == '__main__':
    unittest.main()
