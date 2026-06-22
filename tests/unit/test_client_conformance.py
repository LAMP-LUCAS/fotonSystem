"""Tests for ClientConformanceChecker."""

import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_CONFIG_PATH = "foton_system.modules.shared.infrastructure.config.config.Config"


class TestClientConformanceChecker(unittest.TestCase):
    """Tests for folder name, INFO pattern, and conformance fixing."""

    def setUp(self):
        self.temp_dir = Path(__file__).parent / "_test_conformance_temp"
        self.temp_dir.mkdir(exist_ok=True)
        # Clean up any previous test artifacts
        for p in self.temp_dir.iterdir():
            if p.is_dir():
                import shutil
                shutil.rmtree(p)
            else:
                p.unlink()

    def tearDown(self):
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

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


if __name__ == "__main__":
    unittest.main()
