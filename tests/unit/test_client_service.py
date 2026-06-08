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
from unittest.mock import MagicMock, patch, PropertyMock
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
            service.create_client(name='João', alias='Client<>Name')

        self.assertIn('inválidos', str(context.exception))

    def test_create_client_rejects_reserved_names(self):
        """Client creation fails for Windows reserved names."""
        repo = FakeClientRepository()
        service = ClientService(repo)

        with self.assertRaises(ValueError) as context:
            service.create_client(name='Printer', alias='CON')

        self.assertIn('inválidos', str(context.exception))

    def test_create_client_accepts_valid_input(self):
        """Client creation succeeds for valid input."""
        repo = FakeClientRepository()
        service = ClientService(repo)

        result = service.create_client(name='Maria Santos', alias='001_Maria_Santos')

        # Bug #2 fix: create_client now returns CreatedClient dataclass
        self.assertTrue(hasattr(result, 'codigo'))
        self.assertTrue(result.codigo)
        self.assertTrue(hasattr(result, 'caminho'))
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
        from foton_system.modules.clients.application.use_cases.client_validation import format_cpf_cnpj
        
        result = format_cpf_cnpj('123.456.789-00')
        self.assertEqual(result, '12345678900')
        
        result = format_cpf_cnpj('12.345.678/0001-99')
        self.assertEqual(result, '12345678000199')


class TestClientServiceFileParsing(unittest.TestCase):
    """Tests for file parsing and versioning logic."""

    def test_parse_filename_extracts_version_and_revision(self):
        """Parses VER and REV from filename correctly."""
        from foton_system.modules.clients.application.use_cases.client_crud import _parse_filename
        
        mock_path = MagicMock()
        mock_path.stem = 'CODE_DOC_CD_01_R02_INFO-ClientAlias'
        
        ver, rev = _parse_filename(mock_path)
        
        self.assertEqual(ver, '01')
        self.assertEqual(rev, 'R02')

    def test_parse_filename_handles_malformed_names(self):
        """Returns defaults for malformed filenames."""
        from foton_system.modules.clients.application.use_cases.client_crud import _parse_filename
        
        mock_path = MagicMock()
        mock_path.stem = 'InvalidFormat'
        
        ver, rev = _parse_filename(mock_path)
        
        self.assertEqual(ver, '00')
        self.assertEqual(rev, 'R00')


if __name__ == '__main__':
    unittest.main()


class TestNormalizeClientName(unittest.TestCase):
    """Tests for ClientService.normalize_client_name()."""

    def test_normalize_removes_accents(self):
        self.assertEqual(ClientService.normalize_client_name("João"), "JOAO")

    def test_normalize_replaces_spaces_with_underscore(self):
        self.assertEqual(ClientService.normalize_client_name("João Silva"), "JOAO_SILVA")

    def test_normalize_removes_hyphens(self):
        self.assertEqual(ClientService.normalize_client_name("ANTONIO-FERREIRA"), "ANTONIO_FERREIRA")

    def test_normalize_no_double_underscore(self):
        self.assertEqual(ClientService.normalize_client_name("João  Silva"), "JOAO_SILVA")

    def test_normalize_already_upper_snake(self):
        self.assertEqual(ClientService.normalize_client_name("MARIA_SANTOS"), "MARIA_SANTOS")

    def test_normalize_empty_string(self):
        self.assertEqual(ClientService.normalize_client_name(""), "")

    def test_normalize_none_returns_empty(self):
        self.assertEqual(ClientService.normalize_client_name(None), "")

    def test_normalize_preserves_underscore_separator(self):
        self.assertEqual(ClientService.normalize_client_name("B & F Construção"), "B_F_CONSTRUCAO")


class TestListServiceNodes(unittest.TestCase):
    """Tests for ClientService.list_service_nodes()."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.clients_dir = self.temp_dir / "CLIENTES"
        self.clients_dir.mkdir()
        self.config_patcher = patch(
            'foton_system.modules.clients.application.use_cases.client_service.Config'
        )
        self.mock_config_class = self.config_patcher.start()
        self.mock_config = MagicMock()
        self.mock_config.base_pasta_clientes = self.clients_dir
        type(self.mock_config).folder_doc = PropertyMock(return_value='00_DOC')
        type(self.mock_config).folder_adm = PropertyMock(return_value='01_ADM')
        type(self.mock_config).folder_op = PropertyMock(return_value='02_OPERACAO')
        type(self.mock_config).ignored_folders = PropertyMock(
            return_value=['00_DOC', '01_ADM', '02_OPERACAO', 'DOC', 'ARQ', 'HID', 'ELE', 'STR', 'PL', 'EVT']
        )
        self.mock_config_class.return_value = self.mock_config

    def tearDown(self):
        self.config_patcher.stop()
        shutil.rmtree(self.temp_dir)

    def _make_client(self, name):
        path = self.clients_dir / name
        path.mkdir()
        return path

    def _make_service(self, client_name, service_name):
        path = self.clients_dir / client_name / service_name
        path.mkdir(parents=True, exist_ok=True)
        return path

    def test_list_service_nodes_returns_empty_for_no_services(self):
        client = self._make_client("TESTE")
        repo = FakeClientRepository(folders={'TESTE'}, service_folders={'TESTE': set()})
        svc = ClientService(repo)
        # When client has only functional folders, no services should be listed
        (client / '00_DOC').mkdir()
        (client / '01_ADM').mkdir()
        nodes = svc.list_service_nodes("TESTE")
        self.assertEqual(nodes, [])

    def test_list_service_nodes_excludes_functional_folders(self):
        client = self._make_client("TESTE")
        (client / '00_DOC').mkdir()
        (client / '01_ADM').mkdir()
        (client / '02_OPERACAO').mkdir()
        (client / 'REFORMA').mkdir()  # actual service
        repo = FakeClientRepository(folders={'TESTE'}, service_folders={'TESTE': {'REFORMA'}})
        svc = ClientService(repo)
        nodes = svc.list_service_nodes("TESTE")
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0]['name'], 'REFORMA')

    def test_list_service_nodes_decodes_double_underscore(self):
        client = self._make_client("TESTE")
        (client / 'REFORMA').mkdir()
        (client / 'REFORMA__AMPLIACAO').mkdir()  # sub-service
        repo = FakeClientRepository(folders={'TESTE'}, service_folders={'TESTE': {'REFORMA', 'REFORMA__AMPLIACAO'}})
        svc = ClientService(repo)
        nodes = svc.list_service_nodes("TESTE")
        self.assertEqual(len(nodes), 2)
        names = {n['name'] for n in nodes}
        self.assertIn('REFORMA', names)
        self.assertIn('REFORMA__AMPLIACAO', names)

    def test_list_service_nodes_depth_and_parent(self):
        client = self._make_client("TESTE")
        (client / 'REFORMA').mkdir()
        (client / 'REFORMA__AMPLIACAO').mkdir()
        repo = FakeClientRepository(folders={'TESTE'}, service_folders={'TESTE': {'REFORMA', 'REFORMA__AMPLIACAO'}})
        svc = ClientService(repo)
        nodes = svc.list_service_nodes("TESTE")
        node_map = {n['name']: n for n in nodes}
        self.assertEqual(node_map['REFORMA']['depth'], 0)
        self.assertIsNone(node_map['REFORMA']['parent'])
        self.assertEqual(node_map['REFORMA__AMPLIACAO']['depth'], 1)
        self.assertEqual(node_map['REFORMA__AMPLIACAO']['parent'], 'REFORMA')

    def test_list_service_nodes_ignores_dot_prefix_folders(self):
        client = self._make_client("TESTE")
        (client / '_ignored').mkdir()
        (client / 'REFORMA').mkdir()
        repo = FakeClientRepository(folders={'TESTE'}, service_folders={'TESTE': {'_ignored', 'REFORMA'}})
        svc = ClientService(repo)
        nodes = svc.list_service_nodes("TESTE")
        names = {n['name'] for n in nodes}
        self.assertNotIn('_ignored', names)
        self.assertIn('REFORMA', names)
