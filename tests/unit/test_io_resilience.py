"""
IO Resilience and Robustness Tests

Tests edge cases common in OneDrive/cloud environments:
- PermissionError (file locked by another process)
- FileNotFoundError (sync delays)
- Dirty/malformed input data
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from pathlib import Path

from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import ExcelClientRepository
from foton_system.modules.shared.infrastructure.validators import validate_filename, sanitize_filename


class TestIOResilience(unittest.TestCase):
    """Tests for I/O error handling and resilience."""

    @patch('foton_system.modules.clients.infrastructure.repositories.excel_client_repository.pd.read_excel')
    def test_excel_permission_error_is_propagated(self, mock_read):
        """PermissionError from Excel read should be propagated with proper logging."""
        mock_read.side_effect = PermissionError("File is locked by OneDrive")
        
        repo = ExcelClientRepository()
        
        with self.assertRaises(PermissionError):
            repo.get_clients_dataframe()

    @patch('foton_system.modules.clients.infrastructure.repositories.excel_client_repository.pd.read_excel')
    def test_excel_file_not_found_raises(self, mock_read):
        """FileNotFoundError from missing Excel should be propagated."""
        mock_read.side_effect = FileNotFoundError("Excel not found")
        
        repo = ExcelClientRepository()
        
        with self.assertRaises(FileNotFoundError):
            repo.get_clients_dataframe()

    @patch('foton_system.modules.clients.infrastructure.repositories.excel_client_repository.Config')
    def test_folder_creation_handles_permission_error(self, MockConfig):
        """Folder creation should propagate PermissionError gracefully."""
        mock_config = MagicMock()
        mock_config.base_pasta_clientes = Path('/fake/clients')
        MockConfig.return_value = mock_config
        
        repo = ExcelClientRepository()
        
        with patch.object(Path, 'mkdir', side_effect=PermissionError("Access denied")):
            with self.assertRaises(PermissionError):
                repo.create_folder(Path('/protected/folder'))


class TestValidatorRobustness(unittest.TestCase):
    """Tests for filename validation edge cases."""

    def test_validate_filename_rejects_all_invalid_chars(self):
        """All Windows-invalid characters should be rejected."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            with self.subTest(char=char):
                self.assertFalse(validate_filename(f"test{char}name"))

    def test_validate_filename_accepts_unicode(self):
        """Unicode characters (accents, emojis) should be accepted."""
        self.assertTrue(validate_filename("João 🏗️ Arquiteto"))
        self.assertTrue(validate_filename("Résidence Étoile"))
        self.assertTrue(validate_filename("中文客户"))

    def test_validate_filename_rejects_reserved_names(self):
        """Windows reserved names should be rejected."""
        reserved = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM9', 'LPT1', 'LPT9']
        for name in reserved:
            with self.subTest(name=name):
                self.assertFalse(validate_filename(name))

    def test_validate_filename_accepts_reserved_as_substring(self):
        """Reserved names as part of larger name should be accepted."""
        self.assertTrue(validate_filename("CONEXÃO"))
        self.assertTrue(validate_filename("01_AUX_Folder"))
        self.assertTrue(validate_filename("LPT1_Extended"))

    def test_sanitize_removes_invalid_chars(self):
        """Sanitizer should strip all invalid characters."""
        result = sanitize_filename("Client<>:Name/Test\\Bad|Chars?*End")
        self.assertEqual(result, "ClientNameTestBadCharsEnd")

    def test_sanitize_strips_dots_and_spaces(self):
        """Sanitizer should strip leading/trailing dots and spaces."""
        self.assertEqual(sanitize_filename("  .Hidden.File.  "), "Hidden.File")
        self.assertEqual(sanitize_filename("...test..."), "test")


class TestDirtyDataHandling(unittest.TestCase):
    """Tests for handling corrupted/malformed data."""

    def test_empty_string_validation(self):
        """Empty strings should be rejected."""
        self.assertFalse(validate_filename(""))
        self.assertFalse(validate_filename(None))

    def test_whitespace_only_validation(self):
        """Whitespace-only strings should be sanitized to empty."""
        result = sanitize_filename("   ")
        self.assertEqual(result, "")

    def test_very_long_filename_validation(self):
        """Very long filenames should pass validation (Windows handles truncation)."""
        long_name = "A" * 300
        # validate_filename only checks for invalid chars, not length
        self.assertTrue(validate_filename(long_name))


if __name__ == '__main__':
    unittest.main()
