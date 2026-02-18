"""
Comprehensive Tests for DocumentService

Covers:
- Template listing
- Data loading (MD, TXT, JSON parsing)
- System variable injection
- Mathematical expression resolution
- Context data loading (hierarchical folders)
- Key validation
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
import json

from foton_system.modules.documents.application.use_cases.document_service import DocumentService


class FakeDocumentAdapter:
    """Fake adapter for testing without real Word/PowerPoint files."""
    def load_document(self, path):
        return MagicMock()
    
    def replace_text(self, doc, replacements):
        return doc
    
    def save_document(self, doc, path):
        pass


class TestDocumentServiceSystemVariables(unittest.TestCase):
    """Tests for system variable injection."""

    def test_get_system_variables_returns_expected_keys(self):
        """System variables should include DataAtual, LinkCUB, ReferenciaCUB."""
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())
        
        variables = service._get_system_variables()
        
        self.assertIn('@DataAtual', variables)
        self.assertIn('@LinkCUB', variables)
        self.assertIn('@ReferenciaCUB', variables)

    def test_data_atual_is_formatted_correctly(self):
        """@DataAtual should be a full date like '02 de Fevereiro de 2026'."""
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())
        
        variables = service._get_system_variables()
        
        # Should contain 'de' (Portuguese format)
        self.assertIn(' de ', variables['@DataAtual'])


class TestDocumentServiceMathResolution(unittest.TestCase):
    """Tests for mathematical expression resolution."""

    def test_resolve_simple_addition(self):
        """Resolves [calculo: @a + @b] correctly."""
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())
        
        data = {
            '@valA': '100',
            '@valB': '50',
            '@total': '[calculo: @valA + @valB]'
        }
        
        service._resolve_operations(data)
        
        self.assertEqual(data['@total'], '150.00')

    def test_resolve_complex_expression(self):
        """Resolves multiplication and division."""
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())
        
        data = {
            '@price': '100',
            '@qty': '3',
            '@total': '[calculo: @price * @qty]'
        }
        
        service._resolve_operations(data)
        
        self.assertEqual(data['@total'], '300.00')

    def test_resolve_with_brazilian_format(self):
        """Handles Brazilian number format (1.234,56) in calculations."""
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())
        
        data = {
            '@valA': 'R$ 1.000,50',
            '@valB': '500,00',
            '@total': '[calculo: @valA + @valB]'
        }
        
        service._resolve_operations(data)
        
        # Result should be 1500.50 formatted as "1500.50"
        self.assertEqual(data['@total'], '1500.50')

    def test_resolve_handles_invalid_expression(self):
        """Invalid expressions should not crash, just log warning."""
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())
        
        data = {
            '@invalid': '[calculo: @missing + 100]'
        }
        
        # Should not raise
        service._resolve_operations(data)
        
        # Original value may remain unchanged or partially resolved
        self.assertIn('[calculo:', data['@invalid'])


class TestDocumentServiceDataParsing(unittest.TestCase):
    """Tests for data file parsing (MD, TXT, JSON)."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_parse_md_data_extracts_key_values(self):
        """Parses key: value pairs from MD files."""
        md_file = self.test_dir / 'data.md'
        md_file.write_text('@nome: João Silva\n@cpf: 123.456.789-00\n', encoding='utf-8')
        
        result = self.service._parse_md_data(md_file)
        
        self.assertEqual(result['@nome'], 'João Silva')
        self.assertEqual(result['@cpf'], '123.456.789-00')

    def test_parse_txt_data_extracts_semicolon_separated(self):
        """Parses key;value pairs from TXT files."""
        txt_file = self.test_dir / 'data.txt'
        txt_file.write_text('@nome;João Silva\n@cpf;12345678900\n', encoding='utf-8')
        
        result = self.service._parse_txt_data(txt_file)
        
        self.assertEqual(result['@nome'], 'João Silva')
        self.assertEqual(result['@cpf'], '12345678900')

    def test_load_data_handles_json(self):
        """Loads data from JSON files correctly."""
        json_file = self.test_dir / 'data.json'
        json_file.write_text(json.dumps({'@nome': 'Test', '@valor': 100}), encoding='utf-8')
        
        result = self.service._load_data(str(json_file))
        
        self.assertEqual(result['@nome'], 'Test')
        self.assertEqual(result['@valor'], 100)

    def test_load_data_returns_empty_for_missing_file(self):
        """Returns empty dict for non-existent files."""
        result = self.service._load_data('/nonexistent/path.md')
        
        self.assertEqual(result, {})


class TestDocumentServiceKeyExtraction(unittest.TestCase):
    """Tests for template key extraction."""

    def test_extract_keys_finds_at_variables(self):
        """Extracts @variable patterns from text."""
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())
        keys = set()
        
        service._extract_keys_from_text('O cliente @nomeCliente mora em @cidade.', keys)
        
        self.assertIn('@nomeCliente', keys)
        self.assertIn('@cidade', keys)

    def test_extract_keys_handles_percentage(self):
        """Extracts @variable% patterns."""
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())
        keys = set()
        
        service._extract_keys_from_text('Custo é @ArqEng% do total.', keys)
        
        self.assertIn('@ArqEng%', keys)


class TestDocumentServiceTemplates(unittest.TestCase):
    """Tests for template listing."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    def test_list_templates_returns_matching_files(self, MockConfig):
        """list_templates returns only files with specified extension."""
        mock_config = MagicMock()
        mock_config.templates_path = self.test_dir
        MockConfig.return_value = mock_config
        
        # Create sample files
        (self.test_dir / 'template1.docx').touch()
        (self.test_dir / 'template2.docx').touch()
        (self.test_dir / 'other.pptx').touch()
        
        result = self.service.list_templates('docx')
        
        self.assertEqual(len(result), 2)
        self.assertIn('template1.docx', result)
        self.assertIn('template2.docx', result)

    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    def test_list_templates_empty_for_missing_dir(self, MockConfig):
        """Returns empty list if templates directory doesn't exist."""
        mock_config = MagicMock()
        mock_config.templates_path = Path('/nonexistent/path')
        MockConfig.return_value = mock_config
        
        result = self.service.list_templates('docx')
        
        self.assertEqual(result, [])


class TestDocumentServiceCustomDataFile(unittest.TestCase):
    """Tests for custom data file creation."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_creates_data_file_with_template_content(self):
        """create_custom_data_file creates file with default template."""
        result = self.service.create_custom_data_file(self.test_dir, 'ABC123')
        
        self.assertIsNotNone(result)
        self.assertTrue(result.exists())
        content = result.read_text(encoding='utf-8')
        self.assertIn('@TEMPLATE:', content)
        self.assertIn('@valorProposta:', content)

    def test_returns_none_for_missing_path(self):
        """Returns None if client path doesn't exist."""
        result = self.service.create_custom_data_file(Path('/nonexistent'), 'ABC')
        
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
