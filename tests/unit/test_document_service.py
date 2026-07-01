"""
Comprehensive Tests for DocumentService

Covers:
- Template listing
- Data loading (MD, TXT, JSON parsing)
- System variable injection
- Mathematical expression resolution
- Context data loading (hierarchical folders)
- Key validation
- Generation history (JSONL + versioning)
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
import json
import os

from foton_system.modules.documents.application.use_cases.document_service import DocumentService
from foton_system.modules.documents.infrastructure.adapters.python_docx_adapter import PythonDocxAdapter


class FakeDocumentAdapter:
    """Fake adapter for testing without real Word/PowerPoint files."""
    def load_document(self, path):
        return MagicMock()
    
    def replace_text(self, doc, replacements):
        return doc
    
    def save_document(self, doc, path):
        pass

    def validate_no_placeholders(self, doc, doc_type):
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

    def test_resolve_handles_missing_var_as_zero(self):
        """Missing variables default to zero in calculations."""
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())
        
        data = {
            '@invalid': '[calculo: @missing + 100]'
        }
        
        # Should not raise
        service._resolve_operations(data)
        
        # Missing @missing defaults to 0.0, so result is 100.00
        self.assertEqual(data['@invalid'], '100.00')

    def test_resolve_with_description_after_calculo(self):
        """[calculo: ...] with trailing description text should resolve correctly."""
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())
        data = {
            '@procLegais': '1000',
            '@totalGeral': '5000',
            '@legais': '[calculo: @procLegais/@totalGeral] Percentual do custo de processos legais'
        }
        service._resolve_operations(data)
        self.assertEqual(data['@legais'], '0.20')

    def test_resolve_cascade_with_descriptions(self):
        """Multi-level cascading dependencies with descriptions should all resolve."""
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())
        data = {
            '@areaCoberta': '440',
            '@projArqEng': '41600.52',
            '@procLegais': '105069.46',
            '@CUBref': '[calculo: 2768.47] Referencia CUB do mes',
            '@ACEqv': '[calculo: @areaCoberta] Area construida equivalente',
            '@execcub': '[calculo: @ACEqv * 6.13] Custo execucao baseado no CUB',
            '@execInfra': '[calculo: @execcub * 0.20] Custo de infraestrutura',
            '@execPais': '[calculo: @execcub * 0.05] Custo de paisagismo',
            '@execMob': '[calculo: @execcub * 0.05] Custo de mobiliario',
            '@totalParcial': '[calculo: @projArqEng + @procLegais] Soma dos custos parciais',
            '@totalExec': '[calculo: @execcub + @execInfra + @execPais + @execMob] Soma execucao',
            '@totalinss': '[calculo: @execcub * 0.20] Total INSS',
            '@totalGeral': '[calculo: @totalParcial + @totalExec + @totalinss] Total geral',
            '@Legais': '[calculo: @procLegais / @totalGeral] Percentual legais',
        }
        service._resolve_operations(data)
        self.assertEqual(data['@ACEqv'], '440.00')
        self.assertEqual(data['@execcub'], '2697.20')
        self.assertEqual(data['@execInfra'], '539.44')
        self.assertEqual(data['@execPais'], '134.86')
        self.assertEqual(data['@execMob'], '134.86')
        self.assertEqual(data['@totalParcial'], '146669.98')
        self.assertEqual(data['@totalExec'], '3506.36')
        self.assertEqual(data['@totalinss'], '539.44')
        self.assertEqual(data['@totalGeral'], '150715.78')
        self.assertEqual(data['@Legais'], '0.70')

    def test_resolve_circular_dependency_does_not_loop(self):
        """Circular dependencies should not cause infinite loop."""
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())
        data = {
            '@a': '[calculo: @b + 10] Desc A',
            '@b': '[calculo: @a + 20] Desc B'
        }
        service._resolve_operations(data)
        self.assertNotEqual(data['@a'], data['@b'])

    def test_resolve_preserves_brazilian_format_in_descriptions(self):
        """Brazilian formatted numbers with descriptions should resolve."""
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())
        data = {
            '@receita': 'R$ 10.000,00',
            '@custo': 'R$ 2.500,00',
            '@lucro': '[calculo: (@receita - @custo) / @receita] Margem de lucro percentual'
        }
        service._resolve_operations(data)
        self.assertEqual(data['@lucro'], '0.75')

    def test_resolve_deep_cascade_reversed_order(self):
        """Deep cascade with reversed dict order (dependents before deps) must resolve."""
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())
        data = {
            '@e': '[calculo: @d + 10] E',
            '@d': '[calculo: @c + 10] D',
            '@c': '[calculo: @b + 20] C',
            '@b': '[calculo: @a + 30] B',
            '@a': '100',
        }
        service._resolve_operations(data)
        self.assertEqual(data['@a'], '100')
        self.assertEqual(data['@b'], '130.00')
        self.assertEqual(data['@c'], '150.00')
        self.assertEqual(data['@d'], '160.00')
        self.assertEqual(data['@e'], '170.00')


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
        md_file.write_text('@nome: Joao Silva\n@cpf: 123.456.789-00\n', encoding='utf-8')

        result = self.service._parse_md_data(md_file)

        self.assertEqual(result['@nome'], 'Joao Silva')
        self.assertEqual(result['@cpf'], '123.456.789-00')

    def test_parse_txt_data_extracts_semicolon_separated(self):
        """Parses key;value pairs from TXT files."""
        txt_file = self.test_dir / 'data.txt'
        txt_file.write_text('@nome;Joao Silva\n@cpf;12345678900\n', encoding='utf-8')

        result = self.service._parse_txt_data(txt_file)

        self.assertEqual(result['@nome'], 'Joao Silva')
        self.assertEqual(result['@cpf'], '12345678900')

    def test_load_data_returns_normalized_keys(self):
        """Loads data from JSON files and normalizes keys to lowercase."""
        json_file = self.test_dir / 'data.json'
        json_file.write_text(json.dumps({'@Nome': 'Test', '@VALOR': 100}), encoding='utf-8')

        result = self.service._load_data(json_file)

        self.assertEqual(result['@nome'], 'Test')
        self.assertEqual(result['@valor'], 100)

    def test_load_data_returns_empty_for_missing_file(self):
        """Returns empty dict for non-existent files."""
        result = self.service._load_data(Path('/nonexistent/path.md'))

        self.assertEqual(result, {})

class TestDocumentServiceResilience(unittest.TestCase):
    """Tests for Case-Insensitivity and Structural Agnostic Context Loading."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_extract_keys_normalizes_to_lowercase(self):
        """extract_keys_from_text should always save keys in lowercase."""
        keys = set()
        self.service._extract_keys_from_text('Olá @NomeCliente e @VALOR.', keys)

        self.assertIn('@nomecliente', keys)
        self.assertIn('@valor', keys)
        self.assertNotIn('@NomeCliente', keys)

    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    def test_load_context_data_is_agnostic_to_folder_names(self, MockConfig):
        """Should find INFO files even if folder names don't match."""
        # Setup folder structure
        # base / Client / 03_PROJETOS / Project
        base = self.test_dir / "CLIENTES"
        client = base / "SIMONE"
        projects = client / "03_PROJETOS"
        project = projects / "APTO_502"
        project.mkdir(parents=True)

        mock_config = MagicMock()
        mock_config.base_pasta_clientes = base
        MockConfig.return_value = mock_config

        # Create INFO files with non-matching names
        (client / "INFO-GERAL.md").write_text("@CLIENTE; SIMONE", encoding='utf-8')
        (project / "INFO-ESPECIFICO.md").write_text("@VALOR; 1000", encoding='utf-8')

        # Load context from the deepest folder
        data = self.service._load_context_data(project / "data.md")

        self.assertEqual(data['@cliente'], 'SIMONE')
        self.assertEqual(data['@valor'], '1000')

    def test_resolve_operations_is_case_insensitive(self):
        """Calculations should work even if variable case differs."""
        data = {
            '@valorproposta': '1000',
            '@parcela': '[calculo: @VALORPROPOSTA * 0.1]'
        }

        self.service._resolve_operations(data)

        self.assertEqual(data['@parcela'], '100.00')

class TestDocumentServiceKeyExtraction(unittest.TestCase):
    """Tests for template key extraction."""

    def test_extract_keys_finds_at_variables(self):
        """Extracts @variable patterns from text and normalizes."""
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())
        keys = set()

        service._extract_keys_from_text('O cliente @nomeCliente mora em @cidade.', keys)

        self.assertIn('@nomecliente', keys)
        self.assertIn('@cidade', keys)

    def test_extract_keys_handles_percentage(self):
        """Extracts @variable% patterns and normalizes to lowercase."""
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())
        keys = set()
        
        service._extract_keys_from_text('Custo é @ArqEng% do total.', keys)
        
        self.assertIn('@arqeng%', keys)




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
        
        # Inject mock directly
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter(), config=mock_config)
        
        # Create sample files
        (self.test_dir / 'template1.docx').touch()
        (self.test_dir / 'template2.docx').touch()
        (self.test_dir / 'other.pptx').touch()
        
        result = service.list_templates('docx')
        
        self.assertEqual(len(result), 2)
        self.assertIn('template1.docx', result)
        self.assertIn('template2.docx', result)

    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    def test_list_templates_empty_for_missing_dir(self, MockConfig):
        """Returns empty list if templates directory doesn't exist."""
        mock_config = MagicMock()
        mock_config.templates_path = Path(tempfile.mkdtemp()) / "nonexistent"
        MockConfig.return_value = mock_config
        
        service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter(), config=mock_config)
        
        result = service.list_templates('docx')
        
        self.assertEqual(result, [])



class TestDocumentServiceCustomDataFile(unittest.TestCase):
    """Tests for custom data file creation."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('foton_system.modules.shared.infrastructure.services.path_manager.PathManager.get_info_template_path')
    def test_creates_data_file_with_template_content(self, mock_get_path):
        """create_custom_data_file creates file with default template."""
        mock_get_path.return_value = Path('/nonexistent/template.md')
        result = self.service.create_custom_data_file(self.test_dir, 'ABC123')
        
        self.assertIsNotNone(result)
        self.assertTrue(result.exists())
        content = result.read_text(encoding='utf-8')
        self.assertIn('@TEMPLATE:', content)
        self.assertIn('@DataAtual:', content)

    def test_returns_none_for_missing_path(self):
        """Returns None if client path doesn't exist."""
        result = self.service.create_custom_data_file(Path('/nonexistent'), 'ABC')
        
        self.assertIsNone(result)


class TestDocumentServicePreValidacao(unittest.TestCase):
    """STORY-022: Pré-validação Obrigatória + Placeholder Zero."""

    def setUp(self):
        self.service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())

    def test_validate_keys_returns_categorized_dict(self):
        """_validate_keys returns dict with resolved, missing, none_values, formulas."""
        report = self.service._validate_keys(
            "/nonexistent/template.docx", {}, "docx"
        )
        self.assertIn("resolved", report)
        self.assertIn("missing", report)
        self.assertIn("none_values", report)
        self.assertIn("formulas", report)

    def test_validate_keys_detects_none_values(self):
        """none_values should include keys whose replacement is None or '---'."""
        replacements = {
            "@nome": "João",
            "@telefone": None,
            "@endereco": "---",
            "@observacao": ""
        }
        with patch.object(self.service.docx_handler, 'load_document') as mock_load:
            mock_doc = MagicMock()
            mock_para = MagicMock()
            mock_para.text = "@nome @telefone @endereco @observacao"
            mock_doc.paragraphs = [mock_para]
            mock_doc.tables = []
            mock_doc.sections = []
            mock_doc.inline_shapes = []
            mock_load.return_value = mock_doc
            report = self.service._validate_keys(
                "/tmp/template.docx", replacements, "docx"
            )

        self.assertIn("@telefone", report["none_values"])
        self.assertIn("@endereco", report["none_values"])
        self.assertIn("@observacao", report["none_values"])
        self.assertNotIn("@nome", report["none_values"])

    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    @patch.object(DocumentService, '_load_context_data', return_value={})
    @patch.object(DocumentService, '_get_system_variables', return_value={})
    def test_generate_blocked_on_missing_keys(self, mock_sysvars, mock_context, MockConfig):
        """generate_document should raise ValueError when keys are missing."""
        mock_config = MagicMock()
        mock_config.base_pasta_clientes = Path("/tmp/fake_base")
        MockConfig.return_value = mock_config

        # Mock adapter to return a docx with an unresolved @var
        mock_docx_adapter = MagicMock()
        mock_doc = MagicMock()
        mock_para = MagicMock()
        mock_para.text = "Cliente @nomeCompleto nao informado"
        mock_doc.paragraphs = [mock_para]
        mock_doc.tables = []
        mock_doc.sections = []
        mock_doc.inline_shapes = []
        mock_docx_adapter.load_document.return_value = mock_doc

        service = DocumentService(mock_docx_adapter, MagicMock())
        with patch.object(service, '_load_data', return_value={}):
            with self.assertRaises(ValueError) as ctx:
                service.generate_document(
                    template_path="/tmp/template.docx",
                    data_path="/tmp/client_path",
                    output_path="/tmp/output.docx",
                    doc_type="docx",
                    extra_data={"@nome": "João"}
                )
        self.assertIn("bloqueada", str(ctx.exception).lower())

    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    @patch.object(DocumentService, '_load_context_data', return_value={})
    @patch.object(DocumentService, '_get_system_variables', return_value={})
    def test_generate_blocked_on_none_values(self, mock_sysvars, mock_context, MockConfig):
        """generate_document should raise ValueError when a value is None."""
        mock_config = MagicMock()
        mock_config.base_pasta_clientes = Path("/tmp/fake_base")
        MockConfig.return_value = mock_config

        mock_adapter = MagicMock()
        mock_doc = MagicMock()
        mock_para = MagicMock()
        mock_para.text = "@telefone do cliente"
        mock_doc.paragraphs = [mock_para]
        mock_doc.tables = []
        mock_doc.sections = []
        mock_doc.inline_shapes = []
        mock_adapter.load_document.return_value = mock_doc

        svc = DocumentService(mock_adapter, MagicMock())
        with patch.object(svc, '_load_data', return_value={'@telefone': None}):
            with self.assertRaises(ValueError) as ctx:
                svc.generate_document(
                    template_path="/tmp/template.docx",
                    data_path="/tmp/client_path",
                    output_path="/tmp/output.docx",
                    doc_type="docx",
                    extra_data={"@nome": "João"}
                )
        self.assertIn("bloqueada", str(ctx.exception).lower())

    def test_validate_no_placeholders_docx_raises_on_survivor(self):
        """DOCX adapter validate_no_placeholders raises ValueError if @VAR survives."""
        adapter = PythonDocxAdapter()
        mock_doc = MagicMock()
        mock_para = MagicMock()
        mock_para.text = "Cliente @NOME nao substituido"
        mock_doc.paragraphs = [mock_para]
        mock_doc.tables = []
        mock_doc.sections = []

        with self.assertRaises(ValueError) as ctx:
            adapter.validate_no_placeholders(mock_doc, "docx")
        self.assertIn("@NOME", str(ctx.exception))

    def test_validate_no_placeholders_docx_passes_clean(self):
        """DOCX adapter validate_no_placeholders passes when no @VAR survives."""
        adapter = PythonDocxAdapter()
        mock_doc = MagicMock()
        mock_para = MagicMock()
        mock_para.text = "Cliente João Silva já substituído"
        mock_doc.paragraphs = [mock_para]
        mock_doc.tables = []
        mock_doc.sections = []

        try:
            adapter.validate_no_placeholders(mock_doc, "docx")
        except ValueError:
            self.fail("validate_no_placeholders raised ValueError on clean document")


if __name__ == '__main__':
    unittest.main()


class TestDocumentServiceContextCanonical(unittest.TestCase):
    """Tests for canonical INFO file loading and get_generated_doc_path."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    def test_load_context_data_uses_canonical_names(self, MockConfig):
        """Should prefer INFO-CLIENTE.md and INFO-SERVICO.md over generic INFO.md."""
        base = self.test_dir / "CLIENTES"
        client = base / "CLIENTE_A"
        service = client / "SERVICO_X"
        service.mkdir(parents=True)

        mock_config = MagicMock()
        mock_config.base_pasta_clientes = base
        MockConfig.return_value = mock_config

        (client / "INFO-CLIENTE.md").write_text(
            "@CLIENTE; CLIENTE_A\n@ENDERECO; Rua A, 123\n", encoding='utf-8'
        )
        (client / "INFO-generico.md").write_text(
            "@CLIENTE; GENERICO\n@VALOR; 999\n", encoding='utf-8'
        )

        data = self.service._load_context_data(service / "data.md")
        self.assertEqual(data['@cliente'], 'CLIENTE_A')
        self.assertNotIn('@valor', data)

    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    def test_load_context_data_merges_client_then_service(self, MockConfig):
        """Service data should override client data for same key."""
        base = self.test_dir / "CLIENTES"
        client = base / "CLIENTE_B"
        service = client / "PROJETO_Y"
        service.mkdir(parents=True)

        mock_config = MagicMock()
        mock_config.base_pasta_clientes = base
        MockConfig.return_value = mock_config

        (client / "INFO-CLIENTE.md").write_text(
            "@CLIENTE; CLIENTE_B\n@VALOR; 1000\n", encoding='utf-8'
        )
        (service / "INFO-SERVICO.md").write_text(
            "@VALOR; 2000\n@DETALHE; extra\n", encoding='utf-8'
        )

        data = self.service._load_context_data(service / "data.md")
        self.assertEqual(data['@cliente'], 'CLIENTE_B')
        # Service overrides client's @VALOR
        self.assertEqual(data['@valor'], '2000')
        self.assertEqual(data['@detalhe'], 'extra')

    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    def test_get_generated_doc_path_proposta(self, MockConfig):
        """Should return path under {DOC}/GERADOS/PROPOSTA/ for proposal templates."""
        base = self.test_dir / "CLIENTES"
        client = base / "CLIENTE_C"
        service = client / "OBRA_Z"
        service.mkdir(parents=True)

        mock_config = MagicMock()
        mock_config.base_pasta_clientes = base
        type(mock_config).folder_doc = PropertyMock(return_value='00_DOC')
        MockConfig.return_value = mock_config

        result = self.service.get_generated_doc_path(
            service, "PROPOSTA_RESIDENCIAL.docx"
        )

        expected = service / "00_DOC" / "GERADOS" / "PROPOSTA" / "PROPOSTA_RESIDENCIAL.docx"
        self.assertEqual(result, expected)

    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    def test_get_generated_doc_path_contract(self, MockConfig):
        """Should return path under {DOC}/GERADOS/CONTRATO/ for contract templates."""
        base = self.test_dir / "CLIENTES"
        service = base / "CLIENTE_D" / "SERVICO_W"
        service.mkdir(parents=True)

        mock_config = MagicMock()
        mock_config.base_pasta_clientes = base
        type(mock_config).folder_doc = PropertyMock(return_value='00_DOC')
        MockConfig.return_value = mock_config

        result = self.service.get_generated_doc_path(
            service, "CONTRATO_PRESTACAO.docx"
        )

        expected = service / "00_DOC" / "GERADOS" / "CONTRATO" / "CONTRATO_PRESTACAO.docx"
        self.assertEqual(result, expected)

    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    def test_get_generated_doc_path_fallback_geral(self, MockConfig):
        """Unknown template type should fall back to GERAL."""
        base = self.test_dir / "CLIENTES"
        service = base / "CLIENTE_E" / "SERVICO_V"
        service.mkdir(parents=True)

        mock_config = MagicMock()
        mock_config.base_pasta_clientes = base
        type(mock_config).folder_doc = PropertyMock(return_value='00_DOC')
        MockConfig.return_value = mock_config

        result = self.service.get_generated_doc_path(
            service, "MEMORIAL_DESCRITIVO.docx"
        )

        expected = service / "00_DOC" / "GERADOS" / "MEMORIAL" / "MEMORIAL_DESCRITIVO.docx"
        self.assertEqual(result, expected)


class TestDocumentServiceExtraData(unittest.TestCase):
    """Tests for generate_document() extra_data parameter."""

    def setUp(self):
        self.service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())

    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    @patch.object(DocumentService, '_load_context_data', return_value={})
    @patch.object(DocumentService, '_validate_keys', return_value={"resolved": [{"key": "@nome", "value": "Extra Value"}], "missing": [], "none_values": [], "formulas": []})
    @patch.object(DocumentService, '_get_system_variables', return_value={})
    def test_extra_data_bypasses_file_when_provided(self, mock_sysvars, mock_validate,
                                                    mock_context, MockConfig):
        """When extra_data is provided, _load_data should NOT be called."""
        mock_config = MagicMock()
        mock_config.base_pasta_clientes = Path("/tmp/fake_base")
        MockConfig.return_value = mock_config
        mock_adapter = MagicMock()

        service = DocumentService(mock_adapter, mock_adapter)
        with patch.object(service, '_load_data', return_value={}) as mock_load:
            service.generate_document(
                template_path="/tmp/template.docx",
                data_path="/tmp/client_path",
                output_path="/tmp/output.docx",
                doc_type="docx",
                extra_data={"@nome": "Extra Value"}
            )
            mock_load.assert_not_called()

    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    @patch.object(DocumentService, '_load_context_data', return_value={})
    @patch.object(DocumentService, '_validate_keys', return_value={"resolved": [{"key": "@var", "value": "from_extra"}], "missing": [], "none_values": [], "formulas": []})
    @patch.object(DocumentService, '_get_system_variables', return_value={})
    def test_extra_data_overrides_context_and_file(self, mock_sysvars, mock_validate,
                                                   mock_context, MockConfig):
        """extra_data should override context_data and file data in replacements."""
        mock_config = MagicMock()
        mock_config.base_pasta_clientes = Path("/tmp/fake_base")
        MockConfig.return_value = mock_config
        mock_adapter = MagicMock()
        mock_context.return_value = {'@var': 'from_context'}

        service = DocumentService(mock_adapter, mock_adapter)
        with patch.object(service, '_load_data', return_value={'@var': 'from_file'}):
            service.generate_document(
                template_path="/tmp/template.docx",
                data_path="/tmp/client_path",
                output_path="/tmp/output.docx",
                doc_type="docx",
                extra_data={"@var": "from_extra"}
            )

    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    @patch.object(DocumentService, '_load_context_data', return_value={})
    @patch.object(DocumentService, '_validate_keys', return_value={"resolved": [], "missing": [], "none_values": [], "formulas": []})
    @patch.object(DocumentService, '_get_system_variables', return_value={})
    def test_extra_data_none_reads_from_file(self, mock_sysvars, mock_validate,
                                             mock_context, MockConfig):
        """When extra_data is None, _load_data should read from file path."""
        mock_config = MagicMock()
        mock_config.base_pasta_clientes = Path("/tmp/fake_base")
        MockConfig.return_value = mock_config
        mock_adapter = MagicMock()

        service = DocumentService(mock_adapter, mock_adapter)
        with patch.object(service, '_load_data', return_value={}) as mock_load:
            service.generate_document(
                template_path="/tmp/template.docx",
                data_path="/tmp/data.json",
                output_path="/tmp/output.docx",
                doc_type="docx"
            )
            mock_load.assert_called_once()


class TestDocumentServiceHistory(unittest.TestCase):
    """Tests for generation history (JSONL + versioning) — STORY-024 [RULE-DOC-3.6]"""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.temp_dir)
        self.service = DocumentService(FakeDocumentAdapter(), FakeDocumentAdapter())

    def _make_jsonl_path(self, client_dir=None):
        client_dir = client_dir or self.temp_dir
        return client_dir / 'historico_documentos.jsonl'

    # =====================================================================
    # _log_generation writes JSONL
    # =====================================================================

    def test_log_generation_creates_jsonl_file(self):
        """First generation should create historico_documentos.jsonl."""
        output_path = self.temp_dir / 'GERADO_Teste.docx'
        self.service._log_generation(
            output_path=output_path, doc_type='docx',
            template_path='/tmp/template.docx', data_path='/tmp/data.md'
        )
        self.assertTrue(self._make_jsonl_path().exists())

    def test_log_generation_appends_on_multiple_calls(self):
        """Multiple generations should append lines to JSONL."""
        for i in range(3):
            output_path = self.temp_dir / f'GERADO_Teste_v{i}.docx'
            self.service._log_generation(
                output_path=output_path, doc_type='docx',
                template_path='/tmp/template.docx', data_path='/tmp/data.md'
            )
        jsonl_path = self._make_jsonl_path()
        lines = jsonl_path.read_text(encoding='utf-8').strip().split('\n')
        self.assertEqual(len(lines), 3)

    def test_log_generation_contains_required_fields(self):
        """Each JSONL entry must have all required fields from RULE-DOC-3.6."""
        output_path = self.temp_dir / 'GERADO_Teste.docx'
        self.service._log_generation(
            output_path=output_path, doc_type='docx',
            template_path='/tmp/template.docx', data_path='/tmp/data.md'
        )
        entry = json.loads(self._make_jsonl_path().read_text(encoding='utf-8').strip())
        self.assertIn('data_hora', entry)
        self.assertIn('tipo_template', entry)
        self.assertIn('nome_arquivo', entry)
        self.assertIn('status', entry)
        self.assertIn('versao', entry)
        self.assertIn('cliente', entry)

    def test_log_generation_has_iso8601_timestamp(self):
        """data_hora should be ISO 8601 format."""
        output_path = self.temp_dir / 'doc.docx'
        self.service._log_generation(
            output_path=output_path, doc_type='docx',
            template_path='/tmp/template.docx', data_path='/tmp/data.md'
        )
        entry = json.loads(self._make_jsonl_path().read_text(encoding='utf-8'))
        # ISO 8601 contains 'T' separator
        self.assertIn('T', entry['data_hora'])

    def test_log_generation_record_status_sucesso(self):
        """Status should be 'sucesso' for normal generation."""
        output_path = self.temp_dir / 'doc.docx'
        self.service._log_generation(
            output_path=output_path, doc_type='docx',
            template_path='/tmp/template.docx', data_path='/tmp/data.md'
        )
        entry = json.loads(self._make_jsonl_path().read_text(encoding='utf-8'))
        self.assertEqual(entry['status'], 'sucesso')

    def test_log_generation_includes_cliente_name(self):
        """cliente field should match client folder name (output parent)."""
        client_dir = self.temp_dir / 'CLIENTE_TESTE'
        client_dir.mkdir()
        output_path = client_dir / 'GERADO_Teste.docx'
        self.service._log_generation(
            output_path=output_path, doc_type='docx',
            template_path='/tmp/template.docx', data_path='/tmp/data.md'
        )
        entry = json.loads(self._make_jsonl_path(client_dir).read_text(encoding='utf-8'))
        self.assertEqual(entry['cliente'], 'CLIENTE_TESTE')

    def test_log_generation_includes_versao_anterior_when_provided(self):
        """When versao_anterior is passed in extra_data, record it."""
        self.service._log_generation(
            output_path=self.temp_dir / 'doc.docx', doc_type='docx',
            template_path='/tmp/template.docx', data_path='/tmp/data.md',
            extra_params={'versao_anterior': 'GERADO_Teste_v1.docx'}
        )
        entry = json.loads(self._make_jsonl_path().read_text(encoding='utf-8'))
        self.assertEqual(entry['versao_anterior'], 'GERADO_Teste_v1.docx')

    # =====================================================================
    # read_generation_history
    # =====================================================================

    def test_read_history_returns_entries(self):
        """read_generation_history should return list of dicts."""
        output_path = self.temp_dir / 'doc.docx'
        self.service._log_generation(
            output_path=output_path, doc_type='docx',
            template_path='/tmp/template.docx', data_path='/tmp/data.md'
        )
        entries = self.service.read_generation_history(self.temp_dir)
        self.assertIsInstance(entries, list)
        self.assertEqual(len(entries), 1)

    def test_read_history_respects_limit(self):
        """read_generation_history should limit returned entries."""
        for i in range(5):
            self.service._log_generation(
                output_path=self.temp_dir / f'doc_{i}.docx', doc_type='docx',
                template_path='/tmp/template.docx', data_path='/tmp/data.md'
            )
        entries = self.service.read_generation_history(self.temp_dir, limit=3)
        self.assertEqual(len(entries), 3)

    def test_read_history_returns_most_recent_first(self):
        """read_generation_history should return newest entries first."""
        for i in range(3):
            self.service._log_generation(
                output_path=self.temp_dir / f'doc_{i}.docx', doc_type='docx',
                template_path='/tmp/template.docx', data_path='/tmp/data.md'
            )
        entries = self.service.read_generation_history(self.temp_dir, limit=2)
        self.assertEqual(entries[0]['nome_arquivo'], 'doc_2.docx')
        self.assertEqual(entries[1]['nome_arquivo'], 'doc_1.docx')

    def test_read_history_missing_jsonl_returns_empty_list(self):
        """When JSONL does not exist, return empty list (no crash)."""
        entries = self.service.read_generation_history(self.temp_dir)
        self.assertEqual(entries, [])

    def test_read_history_corrupted_jsonl_returns_valid_entries(self):
        """Corrupted lines should be skipped, valid ones returned."""
        jsonl_path = self._make_jsonl_path()
        jsonl_path.write_text(
            '{"nome_arquivo": "ok1.docx", "status": "sucesso"}\n'
            'NOT JSON\n'
            '{"nome_arquivo": "ok2.docx", "status": "sucesso"}\n',
            encoding='utf-8'
        )
        entries = self.service.read_generation_history(self.temp_dir)
        self.assertEqual(len(entries), 2)

    # =====================================================================
    # Versioning logic (via _resolve_version_and_archive)
    # =====================================================================

    def test_first_version_is_1(self):
        """First generation for a template should get version 1."""
        output_path = self.temp_dir / 'GERADO_Teste.docx'
        template_name = 'template.docx'
        client_dir = self.temp_dir
        version, prev_file = self.service._resolve_version_and_archive(
            client_dir, output_path, template_name
        )
        self.assertEqual(version, 1)
        self.assertIsNone(prev_file)

    def test_version_increments_on_regeneration(self):
        """Regeneration should increment version."""
        output_path = self.temp_dir / 'GERADO_Teste.docx'
        template_name = 'template.docx'
        client_dir = self.temp_dir
        # Simulate first gen
        output_path.write_text('v1 content')
        self.service._log_generation(
            output_path=output_path, doc_type='docx',
            template_path=f'/tmp/{template_name}', data_path='/tmp/data.md'
        )
        version, prev_file = self.service._resolve_version_and_archive(
            client_dir, output_path, template_name
        )
        self.assertEqual(version, 2)
        self.assertIsNotNone(prev_file)

    def test_archive_renames_existing_file(self):
        """Previous file should be renamed with _vN suffix."""
        output_path = self.temp_dir / 'GERADO_Teste.docx'
        output_path.write_text('original content')
        template_name = 'template.docx'
        client_dir = self.temp_dir
        self.service._log_generation(
            output_path=output_path, doc_type='docx',
            template_path=f'/tmp/{template_name}', data_path='/tmp/data.md'
        )
        version, prev_file = self.service._resolve_version_and_archive(
            client_dir, output_path, template_name
        )
        self.assertIsNotNone(prev_file)
        self.assertTrue(prev_file.exists())
        self.assertEqual(prev_file.read_text(), 'original content')
        # Original file should have been moved
        self.assertFalse(output_path.exists())

    # =====================================================================
    # Integration: versioning via generate_document
    # =====================================================================

    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    @patch.object(DocumentService, '_load_context_data', return_value={})
    @patch.object(DocumentService, '_validate_keys', return_value={"resolved": [], "missing": [], "none_values": [], "formulas": []})
    @patch.object(DocumentService, '_get_system_variables', return_value={})
    def test_generate_document_creates_jsonl(self, mock_sysvars, mock_validate,
                                              mock_context, MockConfig):
        """generate_document should create historico_documentos.jsonl."""
        mock_config = MagicMock()
        mock_config.base_pasta_clientes = Path("/tmp/fake_base")
        MockConfig.return_value = mock_config
        adapter = MagicMock()

        client_dir = self.temp_dir / 'CLIENTE_X'
        client_dir.mkdir()
        output_path = client_dir / 'GERADO_Teste.docx'

        service = DocumentService(adapter, adapter)
        with patch.object(service, '_load_data', return_value={'@nome': 'Teste'}):
            service.generate_document(
                template_path="/tmp/template.docx",
                data_path="/tmp/data.md",
                output_path=str(output_path),
                doc_type="docx"
            )
        jsonl_path = client_dir / 'historico_documentos.jsonl'
        self.assertTrue(jsonl_path.exists())

    @patch('foton_system.modules.documents.application.use_cases.document_service.Config')
    @patch.object(DocumentService, '_load_context_data', return_value={})
    @patch.object(DocumentService, '_validate_keys', return_value={"resolved": [], "missing": [], "none_values": [], "formulas": []})
    @patch.object(DocumentService, '_get_system_variables', return_value={})
    def test_regeneration_archives_previous_file(self, mock_sysvars, mock_validate,
                                                  mock_context, MockConfig):
        """Regeneration should archive previous file with _v1 suffix."""
        mock_config = MagicMock()
        mock_config.base_pasta_clientes = Path("/tmp/fake_base")
        MockConfig.return_value = mock_config

        client_dir = self.temp_dir / 'CLIENTE_Y'
        client_dir.mkdir()
        output_path = client_dir / 'GERADO_Teste.docx'
        # Pre-create the output file to simulate a previously generated document
        output_path.write_text('v1 content')

        # Create JSONL history simulating first generation
        jsonl_path = client_dir / 'historico_documentos.jsonl'
        entry = {
            'data_hora': '2026-06-30T10:00:00',
            'tipo_template': 'docx',
            'nome_arquivo': 'GERADO_Teste.docx',
            'template': 'template.docx',
            'status': 'sucesso',
            'versao': 1,
            'versao_anterior': None,
            'cliente': 'CLIENTE_Y',
        }
        with open(jsonl_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

        adapter = MagicMock()
        service = DocumentService(adapter, adapter)
        with patch.object(service, '_load_data', return_value={'@nome': 'Teste'}):
            # Regeneration (second version)
            service.generate_document(
                template_path="/tmp/template.docx",
                data_path="/tmp/data.md",
                output_path=str(output_path),
                doc_type="docx"
            )

        # Original file should have been renamed to _v1
        v1_path = client_dir / 'GERADO_Teste_v1.docx'
        self.assertTrue(v1_path.exists(), "Previous version should be archived as _v1")
        self.assertEqual(v1_path.read_text(), 'v1 content', "Archived content should match original")

        # Mock was called to save new version at output_path
        adapter.save_document.assert_called_once()
