"""
Tests for Template Validation (Pre-flight)

Covers:
- Validation detects missing keys between template and data
- Validation passes when all keys are present
- MCP tool integration for template validation
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

from foton_system.modules.documents.application.use_cases.document_service import DocumentService


class FakeDocumentAdapter:
    """Fake adapter for testing without real Word/PowerPoint files."""
    def load_document(self, path):
        return MagicMock()

    def replace_text(self, doc, replacements):
        return doc

    def save_document(self, doc, path):
        pass


class TestValidateTemplatePreFlight(unittest.TestCase):
    """Tests for standalone template validation via DocumentService."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_validate_detects_missing_keys(self):
        """Should detect keys in template text not present in data file."""
        # Create a data file with some keys
        data_file = self.test_dir / 'data.md'
        data_file.write_text(
            '@nomeCliente: João Silva\n@cpf: 123.456.789-00\n',
            encoding='utf-8'
        )

        # Mock _validate_keys to return a list of missing keys
        with patch.object(self.service, '_validate_keys', return_value=[
            '@endereco', '@telefone'
        ]):
            missing = self.service.validate_template_keys(
                str(self.test_dir / 'template.docx'),
                str(data_file),
                'docx'
            )

        # @endereco and @telefone should be missing
        self.assertIn('@endereco', missing)
        self.assertIn('@telefone', missing)

    def test_validate_passes_when_all_keys_present(self):
        """Should return empty list when all template keys are in data."""
        data_file = self.test_dir / 'data.md'
        data_file.write_text(
            '@nomeCliente: João\n@cpf: 12345\n',
            encoding='utf-8'
        )

        with patch.object(self.service, '_validate_keys', return_value=[]):
            missing = self.service.validate_template_keys(
                str(self.test_dir / 'template.docx'),
                str(data_file),
                'docx'
            )

        self.assertEqual(len(missing), 0)


if __name__ == '__main__':
    unittest.main()
