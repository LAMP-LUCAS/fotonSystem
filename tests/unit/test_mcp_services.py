"""
MCP Services Layer Tests

Tests that use proper dependency injection to verify MCPServices logic.
All tests use fakes injected via constructor - no patching required.
"""

import unittest
from unittest.mock import MagicMock
from pathlib import Path


class FakeConfig:
    """Fake configuration for testing."""
    def __init__(self, base_path=None, templates_path=None):
        self.base_pasta_clientes = Path(base_path) if base_path else Path('/fake/clients')
        self.templates_path = Path(templates_path) if templates_path else Path('/fake/templates')
        self.base_dados = Path('/fake/baseDados.xlsx')
        self.ignored_folders = ['DOC', 'ARQ', 'HID', 'ELE', 'STR', 'PL', 'EVT']
        self.clean_missing_variables = True
        self.missing_variable_placeholder = '---'


class FakeClientService:
    """Fake domain ClientService for testing MCPClientService."""
    def __init__(self, config=None):
        self.clients = {}
        self.services = {}
        self._config = config

    def resolve_client_path(self, client_name):
        for name, info in self.clients.items():
            if client_name.lower() in name.lower():
                return info['path']
        raise ValueError(f"Client '{client_name}' not found.")

    @staticmethod
    def normalize_client_name(name):
        if not name:
            return ""
        import unicodedata, re
        normalized = unicodedata.normalize('NFKD', name)
        normalized = normalized.encode('ascii', 'ignore').decode('ascii')
        normalized = normalized.upper()
        normalized = re.sub(r'[-\s]+', '_', normalized)
        normalized = re.sub(r'[^A-Z0-9_]', '', normalized)
        normalized = re.sub(r'_+', '_', normalized)
        normalized = normalized.strip('_')
        return normalized

    def list_service_nodes(self, client_name):
        client_path = self.resolve_client_path(client_name)
        if not client_path.exists():
            return []
        ignored = set()
        nodes = []
        for entry in sorted(client_path.iterdir()):
            if not entry.is_dir():
                continue
            if entry.name.startswith('_'):
                continue
            if entry.name in ignored:
                continue
            parts = entry.name.split('__')
            depth = len(parts) - 1
            parent = parts[0] if depth >= 1 else None
            nodes.append({
                'name': entry.name,
                'path': entry,
                'depth': depth,
                'parent': parent,
            })
        return nodes

    def sync_clients_db_from_folders(self):
        pass

    def sync_client_folders_from_db(self):
        pass

    def sync_services_db_from_folders(self):
        pass

    def sync_service_folders_from_db(self, client_alias=None):
        pass

    def create_client(self, name, tax_id='', email='', phone='', alias=''):
        from foton_system.modules.clients.application.use_cases.client_service import CreatedClient
        return CreatedClient(codigo='AB01', caminho=Path('/fake/clients') / name, dados={'NomeCliente': name})

    def export_client_data(self):
        pass

    def export_service_data(self):
        pass

    def import_service_data(self):
        pass

    def list_clients(self):
        if not self._config:
            return []
        ignored = set(self._config.ignored_folders + ['.obsidian'])
        base = self._config.base_pasta_clientes
        if not base.exists():
            return []
        clients = []
        for d in sorted(base.iterdir()):
            if d.is_dir() and d.name not in ignored:
                info_files = list(d.glob("*INFO*.md"))
                services = [
                    s.name for s in d.iterdir()
                    if s.is_dir() and s.name not in ignored
                ]
                clients.append({
                    'name': d.name,
                    'has_info': len(info_files) > 0,
                    'service_count': len(services),
                    'services': services,
                })
        return clients

    def read_client_info(self, client_name):
        client_path = self.resolve_client_path(client_name)
        info_files = list(client_path.glob("*INFO*.md"))
        if not info_files:
            raise ValueError(
                f"No INFO file found for '{client_path.name}'.\n"
                f"Expected pattern: *INFO*.md in {client_path}"
            )
        info_file = sorted(info_files, key=lambda f: f.stat().st_mtime, reverse=True)[0]
        content = info_file.read_text(encoding="utf-8")
        return {'filename': info_file.name, 'content': content}

    def update_client_info(self, client_name, section, content):
        import shutil
        client_path = self.resolve_client_path(client_name)
        info_files = list(client_path.glob("*INFO*.md"))
        if not info_files:
            raise ValueError(f"No INFO file found for '{client_path.name}'.")
        info_file = sorted(info_files, key=lambda f: f.stat().st_mtime, reverse=True)[0]

        backup = info_file.with_suffix('.md.bak')
        shutil.copy2(info_file, backup)

        existing = info_file.read_text(encoding="utf-8")
        section_header = f"## {section}"
        if section_header in existing:
            parts = existing.split(section_header, 1)
            after_header = parts[1]
            next_section_idx = after_header.find("\n## ")
            if next_section_idx == -1:
                new_content = existing + f"\n{content}\n"
            else:
                insert_point = len(parts[0]) + len(section_header) + next_section_idx
                new_content = existing[:insert_point] + f"\n{content}\n" + existing[insert_point:]
        else:
            new_content = existing.rstrip() + f"\n\n{section_header}\n{content}\n"

        info_file.write_text(new_content, encoding="utf-8")
        return backup.name


class FakeFinanceService:
    """Fake finance service for testing."""
    def __init__(self):
        self.entries = []
        self.summary = {'saldo': 0.0, 'total_entradas': 0.0, 'total_saidas': 0.0}
        self._by_path = {}

    def add_entry(self, client_path, description, value, entry_type):
        self.entries.append((client_path, description, value, entry_type))
        if entry_type == 'ENTRADA':
            self.summary['total_entradas'] += value
            self.summary['saldo'] += value
        else:
            self.summary['total_saidas'] += value
            self.summary['saldo'] -= value
        result = self.summary.copy()
        self._by_path[str(client_path)] = result
        return result

    def get_summary(self, client_path):
        return self._by_path.get(str(client_path), self.summary.copy())

    def get_firm_summary(self, client_paths):
        results = []
        for p in client_paths:
            s = self.get_summary(p)
            if s['total_entradas'] == 0 and s['total_saidas'] == 0:
                continue
            results.append({
                'name': p.name,
                'income': s['total_entradas'],
                'expense': s['total_saidas'],
                'balance': s['saldo'],
            })
        return results


class FakeDocumentService:
    """Fake document service for testing."""
    def __init__(self):
        self.templates = {'pptx': ['prop.pptx'], 'docx': ['contract.docx']}
        self.validation_results = ['@nomecliente', '@valorproposta']
        self.data_files = ['data1.json', 'data2.txt']
        self.client_data_files = []

    def list_templates(self, doc_type):
        return self.templates.get(doc_type, [])

    def list_data_files(self):
        return self.data_files

    def list_client_data_files(self, client_path):
        return self.client_data_files

    def create_custom_data_file(self, client_path, cod, ver='00', rev='R00', desc='PROPOSTA'):
        return Path(str(client_path)) / f"02-{cod}_DOC_PC_{ver}_{rev}_{desc}.md"

    def validate_template_keys(self, template_path, data_path, doc_type):
        return self.validation_results


class FakeSyncService:
    """Fake sync service for testing."""
    def sync_dashboard(self):
        return 5


class FakeKnowledgeStore:
    """Fake vector store for testing."""
    def __init__(self, results=None):
        self._results = results or {'documents': [[]], 'metadatas': [[]]}

    def query(self, question, n_results=4):
        return self._results


class TestClientPathResolver(unittest.TestCase):
    """Tests for ClientPathResolver."""

    def test_resolve_existing_client(self):
        """Returns path for existing client folder."""
        from foton_system.interfaces.mcp.mcp_services import ClientPathResolver
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            client_path = Path(tmpdir) / 'TestClient'
            client_path.mkdir()

            config = FakeConfig(base_path=tmpdir)
            resolver = ClientPathResolver(config)

            result = resolver.resolve('TestClient')
            self.assertEqual(result, client_path)

    def test_resolve_partial_match(self):
        """Finds client by partial name match."""
        from foton_system.interfaces.mcp.mcp_services import ClientPathResolver
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            client_path = Path(tmpdir) / '730_Residencia_Silva'
            client_path.mkdir()

            config = FakeConfig(base_path=tmpdir)
            resolver = ClientPathResolver(config)

            result = resolver.resolve('Silva')
            self.assertEqual(result.name, '730_Residencia_Silva')

    def test_resolve_not_found_raises(self):
        """Raises ValueError when client not found."""
        from foton_system.interfaces.mcp.mcp_services import ClientPathResolver
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            config = FakeConfig(base_path=tmpdir)
            resolver = ClientPathResolver(config)

            with self.assertRaises(ValueError):
                resolver.resolve('NonExistent')

    def test_resolve_prevents_traversal(self):
        """Sanitizes directory traversal attempts."""
        from foton_system.interfaces.mcp.mcp_services import ClientPathResolver
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            config = FakeConfig(base_path=tmpdir)
            resolver = ClientPathResolver(config)

            with self.assertRaises(ValueError):
                resolver.resolve('../../../etc/passwd')


class TestMCPClientService(unittest.TestCase):
    """Tests for MCPClientService."""

    def test_resolve_client_path_delegates(self):
        """resolve_client_path delegates to domain client service."""
        from foton_system.interfaces.mcp.mcp_services import MCPClientService
        domain = FakeClientService()
        domain.clients['TestClient'] = {'path': Path('/fake/clients/TestClient')}
        svc = MCPClientService(domain)
        result = svc.resolve_client_path('TestClient')
        self.assertEqual(result, Path('/fake/clients/TestClient'))

    def test_list_clients_uses_config(self):
        """list_clients enumerates client folders via config."""
        from foton_system.interfaces.mcp.mcp_services import MCPClientService
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / 'Alpha').mkdir()
            (Path(tmpdir) / 'Beta').mkdir()
            config = FakeConfig(base_path=tmpdir)
            domain = FakeClientService(config=config)
            svc = MCPClientService(domain, config=config)

            clients = svc.list_clients()
            names = [c['name'] for c in clients]
            self.assertIn('Alpha', names)
            self.assertIn('Beta', names)

    def test_list_clients_respects_ignored(self):
        """list_clients excludes ignored folders."""
        from foton_system.interfaces.mcp.mcp_services import MCPClientService
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / 'Alpha').mkdir()
            (Path(tmpdir) / 'DOC').mkdir()
            config = FakeConfig(base_path=tmpdir)
            domain = FakeClientService(config=config)
            svc = MCPClientService(domain, config=config)

            clients = svc.list_clients()
            names = [c['name'] for c in clients]
            self.assertIn('Alpha', names)
            self.assertNotIn('DOC', names)

    def test_read_client_info_returns_content(self):
        """read_client_info reads INFO file content."""
        from foton_system.interfaces.mcp.mcp_services import MCPClientService
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            client_dir = Path(tmpdir) / 'TestClient'
            client_dir.mkdir()
            info_file = client_dir / 'INFO-CLIENTE.md'
            info_file.write_text('@nome; Teste', encoding='utf-8')

            config = FakeConfig(base_path=tmpdir)
            domain = FakeClientService()
            domain.clients['TestClient'] = {'path': client_dir}
            svc = MCPClientService(domain, config=config)

            result = svc.read_client_info('TestClient')
            self.assertIn('filename', result)
            self.assertIn('content', result)
            self.assertEqual(result['filename'], 'INFO-CLIENTE.md')
            self.assertIn('@nome; Teste', result['content'])

    def test_read_client_info_no_info_raises(self):
        """read_client_info raises ValueError when no INFO file."""
        from foton_system.interfaces.mcp.mcp_services import MCPClientService
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            client_dir = Path(tmpdir) / 'NoInfo'
            client_dir.mkdir()
            config = FakeConfig(base_path=tmpdir)
            domain = FakeClientService()
            domain.clients['NoInfo'] = {'path': client_dir}
            svc = MCPClientService(domain, config=config)

            with self.assertRaises(ValueError):
                svc.read_client_info('NoInfo')

    def test_update_client_info_appends_section(self):
        """update_client_info adds a new section to INFO file."""
        from foton_system.interfaces.mcp.mcp_services import MCPClientService
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            client_dir = Path(tmpdir) / 'TestClient'
            client_dir.mkdir()
            info_file = client_dir / 'INFO-CLIENTE.md'
            info_file.write_text('@nome; Teste\n', encoding='utf-8')

            config = FakeConfig(base_path=tmpdir)
            domain = FakeClientService()
            domain.clients['TestClient'] = {'path': client_dir}
            svc = MCPClientService(domain, config=config)

            svc.update_client_info('TestClient', 'Notas', 'Observacao importante.')

            content = info_file.read_text(encoding='utf-8')
            self.assertIn('Notas', content)
            self.assertIn('Observacao importante.', content)

    def test_sync_clients_db_from_folders(self):
        """Delegates to domain."""
        from foton_system.interfaces.mcp.mcp_services import MCPClientService
        domain = FakeClientService()
        svc = MCPClientService(domain)
        result = svc.sync_clients_db_from_folders()
        self.assertIsInstance(result, str)
        self.assertIn('synchronized', result.lower())

    def test_sync_client_folders_from_db(self):
        """Delegates to domain."""
        from foton_system.interfaces.mcp.mcp_services import MCPClientService
        domain = FakeClientService()
        svc = MCPClientService(domain)
        result = svc.sync_client_folders_from_db()
        self.assertIsInstance(result, str)
        self.assertIn('synchronized', result.lower())

    def test_export_client_data(self):
        """Delegates to domain."""
        from foton_system.interfaces.mcp.mcp_services import MCPClientService
        domain = FakeClientService()
        svc = MCPClientService(domain)
        result = svc.export_client_data()
        self.assertIsInstance(result, str)

    def test_export_service_data(self):
        """Delegates to domain."""
        from foton_system.interfaces.mcp.mcp_services import MCPClientService
        domain = FakeClientService()
        svc = MCPClientService(domain)
        result = svc.export_service_data()
        self.assertIsInstance(result, str)

    def test_import_service_data(self):
        """Delegates to domain."""
        from foton_system.interfaces.mcp.mcp_services import MCPClientService
        domain = FakeClientService()
        svc = MCPClientService(domain)
        result = svc.import_service_data()
        self.assertIsInstance(result, str)

    def test_create_client_returns_dict(self):
        """Delegates to domain and returns dict with expected keys."""
        from foton_system.interfaces.mcp.mcp_services import MCPClientService
        domain = FakeClientService()
        svc = MCPClientService(domain)
        result = svc.create_client('NovoCliente', tax_id='123')
        self.assertIsInstance(result, dict)
        self.assertIn('client_id', result)
        self.assertIn('client_path', result)

    def test_list_services(self):
        """list_services enumerates service subdirs."""
        from foton_system.interfaces.mcp.mcp_services import MCPClientService
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            client_dir = Path(tmpdir) / 'TestClient'
            client_dir.mkdir()
            (client_dir / 'Reforma').mkdir()
            (client_dir / 'Projeto').mkdir()

            config = FakeConfig(base_path=tmpdir)
            domain = FakeClientService()
            domain.clients['TestClient'] = {'path': client_dir}
            svc = MCPClientService(domain, config=config)

            services = svc.list_services('TestClient')
            names = [s['name'] for s in services]
            self.assertIn('Reforma', names)
            self.assertIn('Projeto', names)

    def test_list_services_returns_depth_and_parent(self):
        """list_services returns depth/parent for __ hierarchy."""
        from foton_system.interfaces.mcp.mcp_services import MCPClientService
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            client_dir = Path(tmpdir) / 'TestClient'
            client_dir.mkdir()
            (client_dir / 'REFORMA').mkdir()
            (client_dir / 'REFORMA__AMPLIACAO').mkdir()

            config = FakeConfig(base_path=tmpdir)
            domain = FakeClientService()
            domain.clients['TestClient'] = {'path': client_dir}
            svc = MCPClientService(domain, config=config)

            services = svc.list_services('TestClient')
            svc_map = {s['name']: s for s in services}
            self.assertEqual(svc_map['REFORMA']['depth'], 0)
            self.assertIsNone(svc_map['REFORMA']['parent'])
            self.assertEqual(svc_map['REFORMA__AMPLIACAO']['depth'], 1)
            self.assertEqual(svc_map['REFORMA__AMPLIACAO']['parent'], 'REFORMA')

    def test_normalize_client_name_delegates_to_static(self):
        """normalize_client_name is a static method on ClientService."""
        from foton_system.modules.clients.application.use_cases.client_service import ClientService
        self.assertEqual(ClientService.normalize_client_name("João Silva"), "JOAO_SILVA")
        self.assertEqual(ClientService.normalize_client_name("ANTONIO-FERREIRA"), "ANTONIO_FERREIRA")
        self.assertEqual(ClientService.normalize_client_name(""), "")


class TestMCPFinanceService(unittest.TestCase):
    """Tests for MCPFinanceService with injected dependencies."""

    def test_register_entry_success(self):
        """Registers entry and returns updated balance."""
        from foton_system.interfaces.mcp.mcp_services import MCPFinanceService, ClientPathResolver
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            client_path = Path(tmpdir) / 'TestClient'
            client_path.mkdir()

            config = FakeConfig(base_path=tmpdir)
            resolver = ClientPathResolver(config)
            finance = FakeFinanceService()

            service = MCPFinanceService(resolver, finance)
            result = service.register_entry('TestClient', 'Payment', 1000.0, 'ENTRADA')

            self.assertTrue(result.success)
            self.assertEqual(result.balance, 1000.0)

    def test_register_entry_client_not_found(self):
        """Returns error for non-existent client."""
        from foton_system.interfaces.mcp.mcp_services import MCPFinanceService, ClientPathResolver
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            config = FakeConfig(base_path=tmpdir)
            resolver = ClientPathResolver(config)
            finance = FakeFinanceService()

            service = MCPFinanceService(resolver, finance)
            result = service.register_entry('NonExistent', 'Test', 100.0)

            self.assertFalse(result.success)
            self.assertIn('não encontrado', result.message)

    def test_get_summary_success(self):
        """Returns financial summary for client."""
        from foton_system.interfaces.mcp.mcp_services import MCPFinanceService, ClientPathResolver
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            client_path = Path(tmpdir) / 'TestClient'
            client_path.mkdir()

            config = FakeConfig(base_path=tmpdir)
            resolver = ClientPathResolver(config)
            finance = FakeFinanceService()
            finance.summary = {'saldo': 500.0, 'total_entradas': 1000.0, 'total_saidas': 500.0}

            service = MCPFinanceService(resolver, finance)
            result = service.get_summary('TestClient')

            self.assertTrue(result.success)
            self.assertEqual(result.balance, 500.0)

    def test_get_firm_summary(self):
        """Returns firm-wide financial summary via service delegation."""
        from foton_system.interfaces.mcp.mcp_services import MCPFinanceService, ClientPathResolver
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            client_dir = Path(tmpdir) / 'Alpha'
            client_dir.mkdir()

            config = FakeConfig(base_path=tmpdir)
            resolver = ClientPathResolver(config)
            finance = FakeFinanceService()

            # Seed data via service (not raw CSV) — the whole point of DRY
            finance.add_entry(client_dir, 'Pagamento', 1000.0, 'ENTRADA')
            finance.add_entry(client_dir, 'Compra', 200.0, 'SAIDA')

            svc = MCPFinanceService(resolver, finance, config=config)
            results = svc.get_firm_summary()

            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['name'], 'Alpha')
            self.assertEqual(results[0]['income'], 1000.0)
            self.assertEqual(results[0]['expense'], 200.0)
            self.assertEqual(results[0]['balance'], 800.0)


class TestMCPDocumentService(unittest.TestCase):
    """Tests for MCPDocumentService with injected dependencies."""

    def test_list_templates_success(self):
        """Lists available templates."""
        from foton_system.interfaces.mcp.mcp_services import MCPDocumentService
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            config = FakeConfig(templates_path=tmpdir)
            docs = FakeDocumentService()

            service = MCPDocumentService(config, docs)
            result = service.list_templates()

            self.assertTrue(result.success)
            self.assertIn('pptx', result.templates)
            self.assertIn('prop.pptx', result.templates['pptx'])

    def test_validate_template_keys_delegates_to_domain(self):
        """validate_template_keys delegates to the domain DocumentService."""
        from foton_system.interfaces.mcp.mcp_services import MCPDocumentService
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            config = FakeConfig(templates_path=tmpdir)
            docs = FakeDocumentService()

            service = MCPDocumentService(config, docs)
            result = service.validate_template_keys(
                "/path/template.pptx", "/path/data.md", "pptx"
            )

            self.assertIsInstance(result, list)
            self.assertIn('@nomecliente', result)
            self.assertIn('@valorproposta', result)

    def test_validate_template_keys_empty_results(self):
        """Returns empty list when no keys are missing."""
        from foton_system.interfaces.mcp.mcp_services import MCPDocumentService
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            config = FakeConfig(templates_path=tmpdir)
            docs = FakeDocumentService()
            docs.validation_results = []

            service = MCPDocumentService(config, docs)
            result = service.validate_template_keys(
                "/path/template.docx", "/path/data.md", "docx"
            )

            self.assertIsInstance(result, list)
            self.assertEqual(result, [])

    def test_list_data_files_delegates(self):
        """list_data_files delegates to domain."""
        from foton_system.interfaces.mcp.mcp_services import MCPDocumentService
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            config = FakeConfig(templates_path=tmpdir)
            docs = FakeDocumentService()
            service = MCPDocumentService(config, docs)

            result = service.list_data_files()
            self.assertIn('data1.json', result)
            self.assertIn('data2.txt', result)

    def test_list_client_data_files_delegates(self):
        """list_client_data_files delegates to domain."""
        from foton_system.interfaces.mcp.mcp_services import MCPDocumentService
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            config = FakeConfig(templates_path=tmpdir)
            docs = FakeDocumentService()
            docs.client_data_files = ['INFO.md', 'dados.txt']
            service = MCPDocumentService(config, docs)

            result = service.list_client_data_files('/fake/path')
            self.assertEqual(len(result), 2)

    def test_create_custom_data_file_delegates(self):
        """create_custom_data_file delegates to domain."""
        from foton_system.interfaces.mcp.mcp_services import MCPDocumentService
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            config = FakeConfig(templates_path=tmpdir)
            docs = FakeDocumentService()
            service = MCPDocumentService(config, docs)

            result = service.create_custom_data_file('/path', 'ABC123', desc='CONTRATO')
            self.assertIn('ABC123', str(result))
            self.assertIn('CONTRATO', str(result))


class TestMCPKnowledgeService(unittest.TestCase):
    """Tests for MCPKnowledgeService with injected dependencies."""

    def test_query_returns_results(self):
        """Returns formatted knowledge results."""
        from foton_system.interfaces.mcp.mcp_services import MCPKnowledgeService

        store = FakeKnowledgeStore({
            'documents': [['Document 1', 'Document 2']],
            'metadatas': [[{'filename': 'doc1.md'}, {'filename': 'doc2.md'}]]
        })

        service = MCPKnowledgeService(store)
        result = service.query('test question')

        self.assertTrue(result.success)
        self.assertEqual(len(result.documents), 2)
        self.assertEqual(result.sources, ['doc1.md', 'doc2.md'])

    def test_query_empty_results(self):
        """Returns empty list when no results found."""
        from foton_system.interfaces.mcp.mcp_services import MCPKnowledgeService

        store = FakeKnowledgeStore({'documents': [[]], 'metadatas': [[]]})

        service = MCPKnowledgeService(store)
        result = service.query('unknown topic')

        self.assertTrue(result.success)
        self.assertEqual(result.documents, [])

    def test_query_no_store(self):
        """Returns error when store not available."""
        from foton_system.interfaces.mcp.mcp_services import MCPKnowledgeService

        service = MCPKnowledgeService(None)
        result = service.query('test')

        self.assertFalse(result.success)


class TestMCPServiceFactory(unittest.TestCase):
    """Tests for MCPServiceFactory."""

    def setUp(self):
        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory
        MCPServiceFactory.reset()

    def tearDown(self):
        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory
        MCPServiceFactory.reset()

    def test_get_sync_service(self):
        """get_sync_service returns a SyncService instance."""
        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory
        factory = MCPServiceFactory()
        svc = factory.get_sync_service()
        from foton_system.modules.sync.sync_service import SyncService
        self.assertIsInstance(svc, SyncService)

    def test_get_client_service_returns_mcp_wrapper(self):
        """get_client_service returns MCPClientService."""
        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory, MCPClientService
        factory = MCPServiceFactory()
        svc = factory.get_client_service()
        self.assertIsInstance(svc, MCPClientService)

    def test_get_finance_service_returns_mcp_wrapper(self):
        """get_finance_service returns MCPFinanceService."""
        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory, MCPFinanceService
        factory = MCPServiceFactory()
        svc = factory.get_finance_service()
        self.assertIsInstance(svc, MCPFinanceService)

    def test_get_document_service_returns_mcp_wrapper(self):
        """get_document_service returns MCPDocumentService."""
        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory, MCPDocumentService
        factory = MCPServiceFactory()
        svc = factory.get_document_service()
        self.assertIsInstance(svc, MCPDocumentService)


if __name__ == '__main__':
    unittest.main()
