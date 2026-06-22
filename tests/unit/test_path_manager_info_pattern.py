"""
Tests for PathManager factory methods for InfoPatternResolver.

Fase 0.3 — Config + PathManager integration.
"""

import unittest
from unittest.mock import patch, MagicMock

# Config is imported lazily inside PathManager methods,
# so we patch the class at its definition site.
_CONFIG_PATH = 'foton_system.modules.shared.infrastructure.config.config.Config'


class TestPathManagerInfoPattern(unittest.TestCase):
    """PathManager.get_info_pattern, get_info_glob, get_info_header."""

    def _mock_config(self, patterns):
        cfg = MagicMock()
        cfg.info_file_patterns = patterns
        return cfg

    @patch(_CONFIG_PATH)
    def test_get_info_pattern_cliente(self, MockConfig):
        from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
        MockConfig.return_value = self._mock_config({
            'cliente': "INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md",
            'servico': "INFO-SERVICO-{codServico}_{versao}_R{revisao}.md",
        })

        resolver = PathManager.get_info_pattern("cliente")
        from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
        self.assertIsInstance(resolver, InfoPatternResolver)
        self.assertEqual(
            resolver.resolve(codCliente="ABC", versao="01", revisao="02"),
            "INFO-CLIENTE-ABC_01_R02.md"
        )

    @patch(_CONFIG_PATH)
    def test_get_info_pattern_servico(self, MockConfig):
        from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
        MockConfig.return_value = self._mock_config({
            'cliente': "INFO-CLIENTE-{codCliente}.md",
            'servico': "INFO-SERVICO-{codServico}.md",
        })

        resolver = PathManager.get_info_pattern("servico")
        self.assertEqual(
            resolver.resolve(codServico="SV001"),
            "INFO-SERVICO-SV001.md"
        )

    @patch(_CONFIG_PATH)
    def test_get_info_pattern_tipo_invalido_lanca(self, MockConfig):
        from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
        MockConfig.return_value = self._mock_config({'cliente': "INFO-CLIENTE.md"})

        with self.assertRaises(KeyError):
            PathManager.get_info_pattern("invalido")

    @patch(_CONFIG_PATH)
    def test_get_info_glob_cliente(self, MockConfig):
        from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
        MockConfig.return_value = self._mock_config({
            'cliente': "INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md",
        })

        self.assertEqual(
            PathManager.get_info_glob("cliente"),
            "INFO-CLIENTE-*_*_R*.md"
        )

    @patch(_CONFIG_PATH)
    def test_get_info_glob_sem_placeholders(self, MockConfig):
        from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
        MockConfig.return_value = self._mock_config({
            'cliente': "INFO-CLIENTE.md",
        })

        self.assertEqual(PathManager.get_info_glob("cliente"), "INFO-CLIENTE.md")

    @patch(_CONFIG_PATH)
    def test_get_info_header_cliente(self, MockConfig):
        from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
        MockConfig.return_value = self._mock_config({
            'cliente': "INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md",
        })

        self.assertEqual(
            PathManager.get_info_header("cliente"),
            "## INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md"
        )

    @patch(_CONFIG_PATH)
    def test_get_info_header_servico(self, MockConfig):
        from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
        MockConfig.return_value = self._mock_config({
            'servico': "INFO-SERVICO-{codServico}.md",
        })

        self.assertEqual(
            PathManager.get_info_header("servico"),
            "## INFO-SERVICO-{codServico}.md"
        )


if __name__ == "__main__":
    unittest.main()
