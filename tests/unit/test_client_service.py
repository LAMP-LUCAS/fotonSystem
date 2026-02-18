"""
Comprehensive Unit Tests for ClientService

Follows SOLID & DRY principles:
- Uses a FakeRepository (In-Memory) to isolate logic from infrastructure.
- Tests bidirectional sync, code generation, validation, and edge cases.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
import pandas as pd

# Tested Module
from foton_system.modules.clients.application.use_cases.client_service import ClientService
from foton_system.modules.clients.application.ports.client_repository_port import ClientRepositoryPort


class FakeClientRepository(ClientRepositoryPort):
    """
    In-Memory Fake Repository for Unit Tests.
    
    Respects the port interface without hitting real Excel or Filesystem.
    """
    def __init__(self, clients_df=None, services_df=None, folders=None, service_folders=None):
        self._clients = clients_df if clients_df is not None else pd.DataFrame(columns=['Alias', 'NomeCliente', 'CodCliente'])
        self._services = services_df if services_df is not None else pd.DataFrame(columns=['AliasCliente', 'Alias', 'CodServico'])
        self._folders = folders if folders is not None else set()
        self._service_folders = service_folders if service_folders is not None else {}
        self._created_folders = []

    def get_clients_dataframe(self) -> pd.DataFrame:
        return self._clients.copy()

    def get_services_dataframe(self) -> pd.DataFrame:
        return self._services.copy()

    def save_clients(self, df: pd.DataFrame):
        self._clients = df.copy()

    def save_services(self, df: pd.DataFrame):
        self._services = df.copy()

    def list_client_folders(self) -> set:
        return self._folders.copy()

    def list_service_folders(self, client_name: str) -> set:
        return self._service_folders.get(client_name, set()).copy()

    def create_folder(self, path):
        self._created_folders.append(Path(path))


class TestClientServiceSyncLogic(unittest.TestCase):
    """Tests for bidirectional synchronization logic."""

    def test_sync_clients_db_from_folders_adds_new_aliases(self):
        """When folders exist that are not in DB, they should be added."""
        repo = FakeClientRepository(
            clients_df=pd.DataFrame({'Alias': ['ExistingClient']}),
            folders={'ExistingClient', 'NewClient', 'AnotherNewClient'}
        )
        service = ClientService(repo)
        
        service.sync_clients_db_from_folders()
        
        saved_clients = repo._clients
        self.assertIn('NewClient', saved_clients['Alias'].values)
        self.assertIn('AnotherNewClient', saved_clients['Alias'].values)
        self.assertEqual(len(saved_clients), 3)

    def test_sync_clients_db_from_folders_does_nothing_if_all_exist(self):
        """When all folders are already in DB, no changes should occur."""
        repo = FakeClientRepository(
            clients_df=pd.DataFrame({'Alias': ['ClientA', 'ClientB']}),
            folders={'ClientA', 'ClientB'}
        )
        service = ClientService(repo)
        
        service.sync_clients_db_from_folders()
        
        self.assertEqual(len(repo._clients), 2)

    @patch('foton_system.modules.clients.application.use_cases.client_service.Config')
    def test_sync_client_folders_from_db_creates_missing_folders(self, MockConfig):
        """When clients in DB don't have folders, folders should be created."""
        mock_config = MagicMock()
        mock_config.base_pasta_clientes = Path('/fake/clients')
        MockConfig.return_value = mock_config
        
        repo = FakeClientRepository(
            clients_df=pd.DataFrame({'Alias': ['ClientA', 'ClientB', 'ClientC']}),
            folders={'ClientA'}  # Only ClientA has a folder
        )
        service = ClientService(repo)
        
        service.sync_client_folders_from_db()
        
        # ClientB and ClientC should have folders created
        created_paths = [str(p) for p in repo._created_folders]
        self.assertTrue(any('ClientB' in p for p in created_paths))
        self.assertTrue(any('ClientC' in p for p in created_paths))


class TestClientServiceCodeGeneration(unittest.TestCase):
    """Tests for client code generation."""

    def test_generate_client_code_basic(self):
        """Generates a 4-char code from name (first 4 alphanumeric chars for ≤2 word names)."""
        repo = FakeClientRepository()
        service = ClientService(repo)
        
        code = service.generate_client_code("Jose Santos")  # ASCII name
        
        self.assertIsNotNone(code)
        self.assertEqual(code, 'JOSE')  # First 4 alphanumeric chars, uppercased

    def test_generate_client_code_long_name(self):
        """Names with >2 words use first 2 chars of first + last word."""
        repo = FakeClientRepository()
        service = ClientService(repo)
        
        code = service.generate_client_code("Jose da Silva")
        
        self.assertEqual(code, 'JOSI')  # Jo + Si

    def test_generate_client_code_avoids_collision(self):
        """If code exists, appends a number suffix."""
        repo = FakeClientRepository(
            clients_df=pd.DataFrame({'Alias': ['test'], 'CodCliente': ['JOSE']})  # Match what would be generated
        )
        service = ClientService(repo)
        
        code = service.generate_client_code("Jose Santos")
        
        self.assertNotEqual(code, 'JOSE')
        self.assertEqual(code, 'JOSE01')  # First collision gets 01 suffix

    def test_generate_client_code_handles_none(self):
        """Returns None for empty or None input."""
        repo = FakeClientRepository()
        service = ClientService(repo)
        
        self.assertIsNone(service.generate_client_code(None))
        self.assertIsNone(service.generate_client_code(''))


class TestClientServiceValidation(unittest.TestCase):
    """Tests for input validation (dirty input handling)."""

    def test_create_client_rejects_invalid_alias(self):
        """Client creation fails for invalid characters in alias."""
        repo = FakeClientRepository()
        service = ClientService(repo)
        
        with self.assertRaises(ValueError) as context:
            service.create_client({'NomeCliente': 'João', 'Alias': 'Client<>Name'})
        
        self.assertIn('inválidos', str(context.exception))

    def test_create_client_rejects_reserved_names(self):
        """Client creation fails for Windows reserved names."""
        repo = FakeClientRepository()
        service = ClientService(repo)
        
        with self.assertRaises(ValueError) as context:
            service.create_client({'NomeCliente': 'Printer', 'Alias': 'CON'})
        
        self.assertIn('inválidos', str(context.exception))

    def test_create_client_accepts_valid_input(self):
        """Client creation succeeds for valid input."""
        repo = FakeClientRepository()
        service = ClientService(repo)
        
        result = service.create_client({'NomeCliente': 'Maria Santos', 'Alias': '001_Maria_Santos'})
        
        self.assertIn('CodCliente', result)
        self.assertEqual(len(repo._clients), 1)


class TestClientServiceEdgeCases(unittest.TestCase):
    """Tests for edge cases and dirty data."""

    def test_sync_handles_nan_in_alias(self):
        """Sync should gracefully skip NaN values in Alias column."""
        repo = FakeClientRepository(
            clients_df=pd.DataFrame({'Alias': ['Client1', None, 'Client2']}),
            folders={'Client1', 'Client2', 'Client3'}
        )
        service = ClientService(repo)
        
        # Should not raise
        service.sync_clients_db_from_folders()
        
        # Client3 should be added
        self.assertIn('Client3', repo._clients['Alias'].values)

    def test_format_cpf_cnpj_extracts_digits(self):
        """CPF/CNPJ formatting extracts only digits."""
        repo = FakeClientRepository()
        service = ClientService(repo)
        
        result = service._format_cpf_cnpj('123.456.789-00')
        self.assertEqual(result, '12345678900')
        
        result = service._format_cpf_cnpj('12.345.678/0001-99')
        self.assertEqual(result, '12345678000199')


class TestClientServiceFileParsing(unittest.TestCase):
    """Tests for file parsing and versioning logic."""

    def test_parse_filename_extracts_version_and_revision(self):
        """Parses VER and REV from filename correctly."""
        repo = FakeClientRepository()
        service = ClientService(repo)
        
        # Simulating a Path object
        mock_path = MagicMock()
        mock_path.stem = 'CODE_DOC_CD_01_R02_INFO-ClientAlias'
        
        ver, rev = service._parse_filename(mock_path)
        
        self.assertEqual(ver, '01')
        self.assertEqual(rev, 'R02')

    def test_parse_filename_handles_malformed_names(self):
        """Returns defaults for malformed filenames."""
        repo = FakeClientRepository()
        service = ClientService(repo)
        
        mock_path = MagicMock()
        mock_path.stem = 'InvalidFormat'
        
        ver, rev = service._parse_filename(mock_path)
        
        self.assertEqual(ver, '00')
        self.assertEqual(rev, 'R00')


if __name__ == '__main__':
    unittest.main()
