"""
Tests for Phase 1 — INFO file creation with configurable naming patterns.

Covers:
  - get_template_sections() returns headers from pattern config
  - criar_estrutura_servico creates INFO file with pattern name
  - pipeline_novo_cliente finds INFO file via glob
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open


_CONFIG_PATH = 'foton_system.modules.shared.infrastructure.config.config.Config'


class TestClientCrudTemplateSections(unittest.TestCase):
    """get_template_sections deve retornar headers do pattern configurado."""

    @patch(_CONFIG_PATH)
    def test_get_template_sections_usa_headers_do_pattern(self, MockConfig):
        """Os headers ## no template devem vir do pattern configurado."""
        cfg = MagicMock()
        cfg.info_file_patterns = {
            'cliente': "INFO-CLIENTE-{codCliente}.md",
            'servico': "INFO-SERVICO-{codServico}.md",
        }
        MockConfig.return_value = cfg

        from foton_system.modules.clients.application.use_cases import client_crud
        client_part, service_part = client_crud.get_template_sections(cfg)

        self.assertIn("## INFO-CLIENTE-{codCliente}.md", client_part)
        self.assertIn("## INFO-SERVICO-{codServico}.md", service_part)

    @patch(_CONFIG_PATH)
    def test_get_template_sections_com_pattern_complexo(self, MockConfig):
        """Pattern com múltiplos placeholders deve gerar header completo."""
        cfg = MagicMock()
        cfg.info_file_patterns = {
            'cliente': "INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md",
            'servico': "INFO-SERVICO-{codServico}_{versao}_R{revisao}.md",
        }
        MockConfig.return_value = cfg

        from foton_system.modules.clients.application.use_cases import client_crud
        client_part, _ = client_crud.get_template_sections(cfg)

        self.assertIn(
            "## INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md",
            client_part
        )

    @patch(_CONFIG_PATH)
    def test_get_template_sections_fallback_para_cliente_template(self, MockConfig):
        """Sem template asset, deve usar CLIENT_TEMPLATE_STR com header correto."""
        cfg = MagicMock(spec=[
            'info_file_patterns', 'get',
            'base_pasta_clientes', 'templates_path',
            'ignored_folders', 'clean_missing_variables',
            'missing_variable_placeholder', 'folder_conventions',
            'folder_doc', 'folder_adm', 'folder_op', 'folder_op_phases',
            'pomodoro_work_time', 'pomodoro_short_break',
            'pomodoro_long_break', 'pomodoro_cycles', 'ui_mode',
            'info_file_patterns',
        ])
        cfg.info_file_patterns = {
            'cliente': "INFO-CLIENTE-{codCliente}.md",
            'servico': "INFO-SERVICO-{codServico}.md",
        }
        cfg.get.return_value = None  # no custom template path
        MockConfig.return_value = cfg

        from foton_system.modules.clients.application.use_cases import client_crud
        with patch('pathlib.Path.exists', return_value=False):
            client_part, service_part = client_crud.get_template_sections(cfg)

            self.assertIn("## INFO-CLIENTE-{codCliente}.md", client_part)
            self.assertIn("## INFO-SERVICO-{codServico}.md", service_part)
            self.assertIn("@dataProposta", client_part)


class TestFotonMCPCriarEstruturaServico(unittest.TestCase):
    """criar_estrutura_servico deve criar INFO file com nome do pattern."""

    @patch(_CONFIG_PATH)
    def test_criar_servico_usaria_pattern_no_nome(self, MockConfig):
        """Teste conceitual: o resolver geraria o nome correto para o serviço."""
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        cfg = MagicMock()
        cfg.info_file_patterns = {
            'servico': "INFO-SERVICO-{codServico}_{versao}_R{revisao}.md",
        }
        MockConfig.return_value = cfg

        resolver = InfoPatternResolver(
            cfg.info_file_patterns['servico']
        )
        nome = resolver.resolve(
            codServico="CLIRES01",
            aliasServico="RESIDENCIAL",
            versao="00",
            revisao="00"
        )
        self.assertEqual(nome, "INFO-SERVICO-CLIRES01_00_R00.md")

    @patch(_CONFIG_PATH)
    def test_criar_servico_header_no_template(self, MockConfig):
        """O header no template copiado deve refletir o pattern."""
        cfg = MagicMock()
        cfg.info_file_patterns = {
            'servico': "INFO-SERVICO-{codServico}_{versao}_R{revisao}.md",
        }
        MockConfig.return_value = cfg

        from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
        header = PathManager.get_info_header("servico")
        self.assertIn("INFO-SERVICO-{codServico}_{versao}_R{revisao}.md", header)


class TestFotonMCPPipelineNovoCliente(unittest.TestCase):
    """pipeline_novo_cliente deve encontrar INFO file via glob."""

    @patch(_CONFIG_PATH)
    def test_busca_info_por_glob_encontra_arquivo(self, MockConfig):
        """O glob pattern deve encontrar INFO-CLIENTE-{codigo}.md."""
        from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
        cfg = MagicMock()
        cfg.info_file_patterns = {
            'cliente': "INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md",
        }
        MockConfig.return_value = cfg

        glob_pattern = PathManager.get_info_glob("cliente")
        self.assertEqual(glob_pattern, "INFO-CLIENTE-*_*_R*.md")

    @patch(_CONFIG_PATH)
    def test_busca_info_por_glob_sem_placeholders(self, MockConfig):
        """Glob sem placeholders retorna o nome literal."""
        from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
        cfg = MagicMock()
        cfg.info_file_patterns = {
            'cliente': "INFO-CLIENTE.md",
        }
        MockConfig.return_value = cfg

        glob_pattern = PathManager.get_info_glob("cliente")
        self.assertEqual(glob_pattern, "INFO-CLIENTE.md")


if __name__ == "__main__":
    unittest.main()
