"""
MCP Services Layer Tests

Tests that use proper dependency injection to verify MCPServices logic.
All tests use mocks injected via constructor - no patching required.
"""

import unittest
from unittest.mock import MagicMock
from pathlib import Path


class FakeConfig:
    """Fake configuration for testing."""
    def __init__(self, base_path=None, templates_path=None):
        self.base_pasta_clientes = Path(base_path) if base_path else Path('/fake/clients')
        self.templates_path = Path(templates_path) if templates_path else Path('/fake/templates')


class FakeFinanceService:
    """Fake finance service for testing."""
    def __init__(self):
        self.entries = []
        self.summary = {'saldo': 0.0, 'total_entradas': 0.0, 'total_saidas': 0.0}
    
    def add_entry(self, client_path, description, value, entry_type):
        self.entries.append((client_path, description, value, entry_type))
        if entry_type == 'ENTRADA':
            self.summary['total_entradas'] += value
            self.summary['saldo'] += value
        else:
            self.summary['total_saidas'] += value
            self.summary['saldo'] -= value
        return self.summary.copy()
    
    def get_summary(self, client_path):
        return self.summary.copy()


class FakeDocumentService:
    """Fake document service for testing."""
    def __init__(self):
        self.templates = {'pptx': ['prop.pptx'], 'docx': ['contract.docx']}
    
    def list_templates(self, doc_type):
        return self.templates.get(doc_type, [])


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
            # Create a client folder
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
            
            # Should sanitize path and fail because 'passwd' doesn't exist
            with self.assertRaises(ValueError):
                resolver.resolve('../../../etc/passwd')


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


if __name__ == '__main__':
    unittest.main()
