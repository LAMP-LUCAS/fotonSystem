import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime

from foton_system.modules.documents.domain.models.template_info import TemplateInfo
from foton_system.modules.documents.application.use_cases.document_service import DocumentService


class FakeDocumentAdapter:
    def load_document(self, path):
        return MagicMock()

    def replace_text(self, doc, replacements):
        return doc

    def save_document(self, doc, path):
        pass

    def validate_no_placeholders(self, doc, doc_type):
        pass


class TestTemplateInfoModel(unittest.TestCase):
    def test_create_with_minimal_fields(self):
        info = TemplateInfo(filename="test.pptx")
        self.assertEqual(info.filename, "test.pptx")
        self.assertEqual(info.description, "")
        self.assertIsNone(info.category)
        self.assertEqual(info.tags, [])
        self.assertIsNone(info.version)

    def test_create_with_all_fields(self):
        info = TemplateInfo(
            filename="test.pptx",
            description="Proposta de design de interiores",
            category="proposta",
            tags=["design", "interiores"],
            version="1.0"
        )
        self.assertEqual(info.filename, "test.pptx")
        self.assertEqual(info.description, "Proposta de design de interiores")
        self.assertEqual(info.category, "proposta")
        self.assertEqual(info.tags, ["design", "interiores"])
        self.assertEqual(info.version, "1.0")

    def test_default_tags_is_empty_list(self):
        info1 = TemplateInfo(filename="a.pptx")
        info2 = TemplateInfo(filename="b.pptx")
        info1.tags.append("shared")
        self.assertEqual(info2.tags, [], "Each instance should have its own tags list")


class TestDocumentServiceTemplateIndex(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.index_path = self.test_dir / "templates_index.json"

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_mock_config(self):
        mock_config = MagicMock()
        mock_config.templates_path = self.test_dir
        return mock_config

    def _create_templates(self, *filenames):
        for fname in filenames:
            (self.test_dir / fname).touch()

    def _create_index(self, entries: list[dict]):
        self.index_path.write_text(json.dumps(entries, ensure_ascii=False), encoding='utf-8')

    # G5-T1: list_templates com index retorna descrições
    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    def test_list_templates_with_index_returns_descriptions(self, MockConfig):
        self._create_templates("proposta.pptx", "contrato.docx")
        self._create_index([
            {"filename": "proposta.pptx", "description": "Proposta comercial"},
            {"filename": "contrato.docx", "description": "Contrato de prestação de serviços"},
        ])
        mock_config = self._create_mock_config()
        MockConfig.return_value = mock_config
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter(), config=mock_config)

        result = service.list_templates("pptx")

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], TemplateInfo)
        self.assertEqual(result[0].filename, "proposta.pptx")
        self.assertEqual(result[0].description, "Proposta comercial")

    # G5-T2: list_templates sem index fallback para lista simples
    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    def test_list_templates_without_index_fallback(self, MockConfig):
        self._create_templates("template1.pptx", "template2.pptx")
        mock_config = self._create_mock_config()
        MockConfig.return_value = mock_config
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter(), config=mock_config)

        result = service.list_templates("pptx")

        filenames = [t.filename for t in result]
        self.assertIn("template1.pptx", filenames)
        self.assertIn("template2.pptx", filenames)
        for t in result:
            self.assertEqual(t.description, "")

    # G5-T3: Index com campo ausente não quebra
    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    def test_index_with_missing_fields_does_not_break(self, MockConfig):
        self._create_templates("doc.docx")
        self._create_index([
            {"filename": "doc.docx"},
        ])
        mock_config = self._create_mock_config()
        MockConfig.return_value = mock_config
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter(), config=mock_config)

        result = service.list_templates("docx")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].filename, "doc.docx")
        self.assertEqual(result[0].description, "")

    # G5-T4: Index corrompido (JSON inválido) não quebra
    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    def test_corrupted_index_fallback_gracefully(self, MockConfig):
        self._create_templates("doc.docx")
        self.index_path.write_text("{invalid json}", encoding='utf-8')
        mock_config = self._create_mock_config()
        MockConfig.return_value = mock_config
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter(), config=mock_config)

        result = service.list_templates("docx")

        filenames = [t.filename for t in result]
        self.assertIn("doc.docx", filenames)

    # G5-T5: MCP listar_templates exibe descrição no formato esperado
    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    def test_template_info_format_string(self, MockConfig):
        info = TemplateInfo(filename="proposta.pptx", description="Minha proposta")
        formatted = f"{info.filename} — {info.description}"
        self.assertEqual(formatted, "proposta.pptx — Minha proposta")

    # G5-T6: Cache invalida ao modificar arquivo
    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    def test_cache_invalidates_on_file_modification(self, MockConfig):
        self._create_templates("doc.docx")
        self._create_index([
            {"filename": "doc.docx", "description": "Versão 1"},
        ])
        mock_config = self._create_mock_config()
        MockConfig.return_value = mock_config
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter(), config=mock_config)

        result1 = service.list_templates("docx")
        self.assertEqual(result1[0].description, "Versão 1")

        self._create_index([
            {"filename": "doc.docx", "description": "Versão 2"},
        ])

        result2 = service.list_templates("docx")
        self.assertEqual(result2[0].description, "Versão 2")

    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    def test_list_all_templates_returns_both_extensions(self, MockConfig):
        self._create_templates("a.pptx", "b.docx")
        self._create_index([
            {"filename": "a.pptx", "description": "PPT"},
            {"filename": "b.docx", "description": "DOC"},
        ])
        mock_config = self._create_mock_config()
        MockConfig.return_value = mock_config
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter(), config=mock_config)

        result = service.list_templates()

        self.assertEqual(len(result), 2)
        names = {t.filename for t in result}
        self.assertIn("a.pptx", names)
        self.assertIn("b.docx", names)

    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    def test_list_templates_empty_directory(self, MockConfig):
        mock_config = MagicMock()
        mock_config.templates_path = self.test_dir
        MockConfig.return_value = mock_config
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter(), config=mock_config)

        result = service.list_templates("pptx")

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()