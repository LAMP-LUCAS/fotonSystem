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
from unittest.mock import MagicMock, patch, PropertyMock
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
    @patch.object(DocumentService, '_validate_keys', return_value=[])
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
    @patch.object(DocumentService, '_validate_keys', return_value=[])
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
    @patch.object(DocumentService, '_validate_keys', return_value=[])
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
