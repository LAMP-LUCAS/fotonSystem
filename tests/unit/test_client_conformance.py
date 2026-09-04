"""Tests for ClientConformanceChecker."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_CONFIG_PATH = "foton_system.modules.shared.infrastructure.config.config.Config"


class TestClientConformanceChecker(unittest.TestCase):
    """Tests for folder name, INFO pattern, and conformance fixing."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _make_config(self, patterns=None):
        cfg = MagicMock()
        cfg.base_pasta_clientes = self.temp_dir
        cfg.ignored_folders = ["00_DOC", "01_ADM", "02_OPERACAO"]
        cfg.info_file_patterns = patterns or {
            "cliente": "INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md",
            "servico": "INFO-SERVICO-{codServico}_{versao}_R{revisao}.md",
        }
        cfg.get.return_value = None
        return cfg

    # ------------------------------------------------------------------
    # check: folder name with spaces
    # ------------------------------------------------------------------

    @patch(_CONFIG_PATH)
    def test_check_identifica_pasta_com_espaco(self, MockConfig):
        """Folder name with spaces should be flagged."""
        client_dir = self.temp_dir / "CLIENTE COM ESPACO"
        client_dir.mkdir()

        cfg = self._make_config()
        MockConfig.return_value = cfg

        from foton_system.modules.clients.application.use_cases.client_conformance import (
            ClientConformanceChecker,
        )
        checker = ClientConformanceChecker(cfg)
        items = checker.check()
        folder_items = [i for i in items if i.tipo == "folder_name"]
        self.assertTrue(any("espaço" in i.description.lower() or "ESPACO" in i.description for i in folder_items))

    # ------------------------------------------------------------------
    # check: missing INFO file
    # ------------------------------------------------------------------

    @patch(_CONFIG_PATH)
    def test_check_identifica_info_ausente(self, MockConfig):
        """Client folder without INFO file should be flagged."""
        client_dir = self.temp_dir / "CLIENTE_SEM_INFO"
        client_dir.mkdir()

        cfg = self._make_config()
        MockConfig.return_value = cfg

        from foton_system.modules.clients.application.use_cases.client_conformance import (
            ClientConformanceChecker,
        )
        checker = ClientConformanceChecker(cfg)
        items = checker.check()
        missing = [i for i in items if i.tipo == "missing_info"]
        self.assertTrue(any("CLIENTE_SEM_INFO" in i.description for i in missing))

    # ------------------------------------------------------------------
    # check: pattern mismatch (legacy name)
    # ------------------------------------------------------------------

    @patch(_CONFIG_PATH)
    def test_check_identifica_info_fora_do_pattern(self, MockConfig):
        """Legacy INFO-CLIENTE.md should be flagged as pattern mismatch."""
        client_dir = self.temp_dir / "CLIENTE_TEST"
        client_dir.mkdir()
        info_file = client_dir / "INFO-CLIENTE.md"
        info_file.write_text("@CodCliente; CT001\n@versao; 00\n", encoding="utf-8")

        cfg = self._make_config()
        MockConfig.return_value = cfg

        from foton_system.modules.clients.application.use_cases.client_conformance import (
            ClientConformanceChecker,
        )
        checker = ClientConformanceChecker(cfg)
        items = checker.check()
        mismatches = [i for i in items if i.tipo == "pattern_mismatch"]
        self.assertTrue(any("INFO-CLIENTE.md" in i.description for i in mismatches))

    # ------------------------------------------------------------------
    # auto_fix: renames legacy file to pattern
    # ------------------------------------------------------------------

    @patch(_CONFIG_PATH)
    def test_auto_fix_renomeia_para_pattern(self, MockConfig):
        """auto_fix should rename legacy INFO-CLIENTE.md to pattern."""
        client_dir = self.temp_dir / "CLIENTE_FIX"
        client_dir.mkdir()
        info_file = client_dir / "INFO-CLIENTE.md"
        info_file.write_text("@CodCliente; FX001\n", encoding="utf-8")

        cfg = self._make_config()
        MockConfig.return_value = cfg

        from foton_system.modules.clients.application.use_cases.client_conformance import (
            ClientConformanceChecker,
        )
        checker = ClientConformanceChecker(cfg)
        items = checker.check()
        mismatch = next((i for i in items if i.tipo == "pattern_mismatch"), None)
        self.assertIsNotNone(mismatch, "Expected a pattern_mismatch item")

        success = checker.auto_fix(mismatch)
        self.assertTrue(success)
        self.assertFalse(info_file.exists())
        # Should now have a file matching the pattern
        pattern_files = list(client_dir.glob("INFO-CLIENTE-*.md"))
        self.assertTrue(len(pattern_files) > 0)

    # ------------------------------------------------------------------
    # accept_state: persists decision
    # ------------------------------------------------------------------

    @patch(_CONFIG_PATH)
    def test_accept_state_persiste_decisao(self, MockConfig):
        """accept_state should suppress the item on subsequent checks."""
        client_dir = self.temp_dir / "CLIENTE_ACCEPT"
        client_dir.mkdir()
        info_file = client_dir / "INFO-CLIENTE.md"
        info_file.write_text("@CodCliente; AC001\n", encoding="utf-8")

        cfg = self._make_config()
        MockConfig.return_value = cfg

        from foton_system.modules.clients.application.use_cases.client_conformance import (
            ClientConformanceChecker,
        )
        checker = ClientConformanceChecker(cfg)
        items = checker.check()
        mismatch = next((i for i in items if i.tipo == "pattern_mismatch"), None)
        self.assertIsNotNone(mismatch)

        # Accept the state
        checker.accept_state(mismatch)

        # New checker instance should suppress it
        checker2 = ClientConformanceChecker(cfg)
        items2 = checker2.check()
        mismatch2 = next((i for i in items2 if i.tipo == "pattern_mismatch"), None)
        self.assertIsNone(mismatch2)

        # Clean up accepted state file
        accepted_file = self.temp_dir / ".conformance_accepted.json"
        if accepted_file.exists():
            accepted_file.unlink()


    # ------------------------------------------------------------------
    # auto_fix: missing_info creates INFO file
    # ------------------------------------------------------------------

    @patch(_CONFIG_PATH)
    def test_auto_fix_cria_info_para_cliente_sem_info(self, MockConfig):
        """auto_fix must create an INFO file for a client with missing_info."""
        import pandas as pd
        client_dir = self.temp_dir / "CLIENTE_NOVO"
        client_dir.mkdir()

        excel_path = self.temp_dir / "baseDados.xlsx"
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            pd.DataFrame({
                'Alias': ['CLIENTE_NOVO'],
                'NomeCliente': ['Cliente Novo Teste'],
                'CodCliente': ['CN001'],
            }).to_excel(writer, sheet_name='baseClientes', index=False)
            pd.DataFrame(columns=['AliasCliente', 'Alias']).to_excel(
                writer, sheet_name='baseServicos', index=False
            )

        cfg = self._make_config()
        cfg.base_dados = excel_path
        MockConfig.return_value = cfg

        from foton_system.modules.clients.application.use_cases.client_conformance import (
            ClientConformanceChecker,
        )
        checker = ClientConformanceChecker(cfg)
        items = checker.check()
        missing = [i for i in items if i.tipo == "missing_info" and "CLIENTE_NOVO" in i.description]
        self.assertTrue(len(missing) > 0, "Expected a missing_info item for CLIENTE_NOVO")

        success = checker.auto_fix(missing[0])
        self.assertTrue(success, "auto_fix should succeed for missing_info")

        # Now an INFO file should exist
        info_files = list(client_dir.glob("*INFO*.md"))
        self.assertTrue(len(info_files) > 0, "INFO file should have been created")

    @patch(_CONFIG_PATH)
    def test_auto_fix_cria_info_para_servico_sem_info(self, MockConfig):
        """auto_fix must create an INFO file for a service with missing_info."""
        import pandas as pd
        client_dir = self.temp_dir / "CLIENTE_SERV"
        client_dir.mkdir()
        service_dir = client_dir / "SERVICO_1"
        service_dir.mkdir()

        excel_path = self.temp_dir / "baseDados_serv.xlsx"
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            pd.DataFrame({
                'Alias': ['CLIENTE_SERV'],
                'NomeCliente': ['Cliente Serv'],
                'CodCliente': ['CS01'],
            }).to_excel(writer, sheet_name='baseClientes', index=False)
            pd.DataFrame({
                'AliasCliente': ['CLIENTE_SERV'],
                'Alias': ['SERVICO_1'],
                'CodServico': ['CSSER01'],
            }).to_excel(writer, sheet_name='baseServicos', index=False)

        cfg = self._make_config()
        cfg.base_dados = excel_path
        MockConfig.return_value = cfg

        from foton_system.modules.clients.application.use_cases.client_conformance import (
            ClientConformanceChecker,
        )
        checker = ClientConformanceChecker(cfg)
        items = checker.check()
        missing = [i for i in items if i.tipo == "missing_info" and "SERVICO_1" in str(i.path)]
        self.assertTrue(len(missing) > 0, "Expected missing_info for service")

        success = checker.auto_fix(missing[0])
        self.assertTrue(success, "auto_fix should succeed for missing service INFO")

        info_files = list(service_dir.glob("*INFO*.md"))
        self.assertTrue(len(info_files) > 0, "Service INFO file should have been created")


    # ------------------------------------------------------------------
    # check: invalid_service_code flagged by conformance checker
    # ------------------------------------------------------------------

    @patch(_CONFIG_PATH)
    @patch("foton_system.modules.clients.infrastructure.repositories.excel_client_repository.ExcelClientRepository")
    def test_check_detecta_codigo_servico_invalido(self, MockRepo, MockConfig):
        """Conformance checker deve detectar códigos de serviço inválidos no DB."""
        import pandas as pd
        client_dir = self.temp_dir / "CLI_A"
        client_dir.mkdir()
        svc_dir = client_dir / "REFORMA"
        svc_dir.mkdir()

        fake_repo = MagicMock()
        fake_repo.get_services_dataframe.return_value = pd.DataFrame({
            'AliasCliente': ['CLI_A'],
            'Alias': ['REFORMA'],
            'CodServico': ['000'],
        })
        MockRepo.return_value = fake_repo

        cfg = self._make_config()
        MockConfig.return_value = cfg

        from foton_system.modules.clients.application.use_cases.client_conformance import (
            ClientConformanceChecker,
        )
        checker = ClientConformanceChecker(cfg)
        items = checker.check()
        code_items = [i for i in items if i.tipo == "invalid_service_code"]
        self.assertTrue(len(code_items) > 0,
                        "Expected invalid_service_code items")

    @patch(_CONFIG_PATH)
    @patch("foton_system.modules.clients.infrastructure.repositories.excel_client_repository.ExcelClientRepository")
    def test_auto_fix_corrige_codigo_servico_invalido(self, MockRepo, MockConfig):
        """auto_fix para invalid_service_code deve corrigir o código."""
        import pandas as pd
        client_dir = self.temp_dir / "CLI_B"
        client_dir.mkdir()
        svc_dir = client_dir / "PROJETO"
        svc_dir.mkdir()

        fake_repo = MagicMock()
        fake_repo.get_services_dataframe.return_value = pd.DataFrame({
            'AliasCliente': ['CLI_B'],
            'Alias': ['PROJETO'],
            'CodServico': ['000'],
        })
        MockRepo.return_value = fake_repo

        cfg = self._make_config()
        MockConfig.return_value = cfg

        from foton_system.modules.clients.application.use_cases.client_conformance import (
            ClientConformanceChecker,
        )
        checker = ClientConformanceChecker(cfg)
        items = checker.check()
        code_items = [i for i in items if i.tipo == "invalid_service_code"]
        self.assertTrue(len(code_items) > 0)

        success = checker.auto_fix(code_items[0])
        self.assertTrue(success, "auto_fix should fix invalid service code")


if __name__ == "__main__":
    unittest.main()
