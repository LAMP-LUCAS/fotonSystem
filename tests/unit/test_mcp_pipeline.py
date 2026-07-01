import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestPipelineEmitirDocumento(unittest.TestCase):
    """D3: Tests for pipeline_emitir_documento [RULE-DOC-3.3]"""

    def setUp(self):
        self.patcher_factory = patch(
            'foton_system.interfaces.mcp.foton_mcp._get_factory'
        )
        self.patcher_config = patch(
            'foton_system.interfaces.mcp.foton_mcp._get_config'
        )
        self.mock_factory = self.patcher_factory.start()
        self.mock_config = self.patcher_config.start()
        self.mock_svc = MagicMock()
        self.mock_factory.return_value.get_client_service.return_value = self.mock_svc

    def tearDown(self):
        self.patcher_factory.stop()
        self.patcher_config.stop()

    def test_pipeline_returns_preflight_output(self):
        mock_path = MagicMock(spec=Path)
        mock_path.name = "CLIENTE_TESTE"
        self.mock_svc.resolve_client_path.return_value = mock_path
        from foton_system.interfaces.mcp.foton_mcp import pipeline_emitir_documento
        result = pipeline_emitir_documento(cliente="CLIENTE_TESTE", nome_template="PROPOSTA")
        self.assertIn("PRE-FLIGHT", result)
        self.assertIn("CLIENTE_TESTE", result)

    def test_pipeline_invalid_dados_extras_raises(self):
        from foton_system.interfaces.mcp.foton_mcp import pipeline_emitir_documento
        result = pipeline_emitir_documento(
            cliente="CLIENTE_TESTE", nome_template="PROPOSTA",
            dados_extras={"@key": [1, 2, 3]}
        )
        self.assertIn("Invalid dados_extras", result)


if __name__ == '__main__':
    unittest.main()
