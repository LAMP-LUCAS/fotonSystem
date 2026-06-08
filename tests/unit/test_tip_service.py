"""Tests for TipService — didactic tips indexed from documentation."""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestTipService(unittest.TestCase):
    """Unit tests for TipService indexing and retrieval."""

    def setUp(self):
        self.temp_root = Path(tempfile.mkdtemp())

    @patch("foton_system.modules.shared.infrastructure.services.tip_service.PathManager")
    def test_get_random_tip_returns_string_when_tips_exist(self, mock_pm):
        docs = self.temp_root / "docs"
        docs.mkdir(parents=True, exist_ok=True)
        (docs / "test.md").write_text(
            "> [!DIDACTIC:TEST] Keep your INFO files updated.\n"
            "> [!DIDACTIC:OTHER] Use templates for consistency.\n",
            encoding="utf-8"
        )
        mock_pm._find_project_root.return_value = self.temp_root
        from foton_system.modules.shared.infrastructure.services.tip_service import TipService
        svc = TipService()
        tip = svc.get_random_tip("TEST")
        self.assertIn(tip, ["Keep your INFO files updated.", "Use templates for consistency."])

    @patch("foton_system.modules.shared.infrastructure.services.tip_service.PathManager")
    def test_get_random_tip_fallback_when_context_missing(self, mock_pm):
        docs = self.temp_root / "docs"
        docs.mkdir(parents=True, exist_ok=True)
        (docs / "test.md").write_text(
            "> [!DIDACTIC:GERAL] General tip here.\n",
            encoding="utf-8"
        )
        mock_pm._find_project_root.return_value = self.temp_root
        from foton_system.modules.shared.infrastructure.services.tip_service import TipService
        svc = TipService()
        tip = svc.get_random_tip("UNKNOWN_CONTEXT")
        self.assertEqual(tip, "General tip here.")

    @patch("foton_system.modules.shared.infrastructure.services.tip_service.PathManager")
    def test_get_random_tip_no_exception_when_docs_missing(self, mock_pm):
        mock_pm._find_project_root.return_value = Path("/nonexistent_path_xyz")
        from foton_system.modules.shared.infrastructure.services.tip_service import TipService
        svc = TipService()
        tip = svc.get_random_tip("ANY")
        self.assertIsInstance(tip, str)

    @patch("foton_system.modules.shared.infrastructure.services.tip_service.PathManager")
    def test_index_captures_didactic_pattern(self, mock_pm):
        docs = self.temp_root / "docs"
        docs.mkdir(parents=True, exist_ok=True)
        (docs / "tips.md").write_text(
            "> [!DIDACTIC:WORKFLOW] Always run validar_template first.\n"
            "> [!DIDACTIC:WORKFLOW] Keep INFO files in sync.\n",
            encoding="utf-8"
        )
        mock_pm._find_project_root.return_value = self.temp_root
        from foton_system.modules.shared.infrastructure.services.tip_service import TipService
        svc = TipService()
        svc._index_tips()
        self.assertIn("Always run validar_template first.", svc._tips_cache.get("WORKFLOW", []))

    @patch("foton_system.modules.shared.infrastructure.services.tip_service.PathManager")
    def test_index_ignores_non_md_files(self, mock_pm):
        docs = self.temp_root / "docs"
        docs.mkdir(parents=True, exist_ok=True)
        (docs / "data.txt").write_text(
            "> [!DIDACTIC:TEST] Should be ignored.\n",
            encoding="utf-8"
        )
        mock_pm._find_project_root.return_value = self.temp_root
        from foton_system.modules.shared.infrastructure.services.tip_service import TipService
        svc = TipService()
        svc._index_tips()
        self.assertNotIn("Should be ignored.", svc._tips_cache.get("TEST", []))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
