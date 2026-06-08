"""Tests for ConfigProvider singleton — folder_conventions properties."""

import unittest
from foton_system.modules.shared.infrastructure.config.config import Config


class TestFolderConventionsDefaults(unittest.TestCase):
    """folder_conventions properties return correct defaults when not set."""

    def setUp(self):
        Config._instance = None
        self.config = Config()
        # Ensure no folder_conventions key to test defaults
        self.config._settings.pop('folder_conventions', None)

    def tearDown(self):
        Config._instance = None

    def test_folder_doc_default(self):
        self.assertEqual(self.config.folder_doc, '00_DOC')

    def test_folder_adm_default(self):
        self.assertEqual(self.config.folder_adm, '01_ADM')

    def test_folder_op_default(self):
        self.assertEqual(self.config.folder_op, '02_OPERACAO')

    def test_folder_op_phases_default(self):
        self.assertEqual(self.config.folder_op_phases, ['EP', 'AP', 'EXE', 'REL'])

    def test_ignored_folders_includes_functional(self):
        ignored = self.config.ignored_folders
        self.assertIn('00_DOC', ignored)
        self.assertIn('01_ADM', ignored)
        self.assertIn('02_OPERACAO', ignored)


class TestFolderConventionsCustom(unittest.TestCase):
    """folder_conventions properties reflect custom settings."""

    def setUp(self):
        Config._instance = None
        self.config = Config()
        self.config._settings['folder_conventions'] = {
            'doc': '_DOCS',
            'adm': 'ADMIN',
            'op': '_PRODUCAO',
            'op_phases': ['VIAB', 'PROJ', 'OBRA'],
        }

    def tearDown(self):
        Config._instance = None

    def test_folder_doc_custom(self):
        self.assertEqual(self.config.folder_doc, '_DOCS')

    def test_folder_adm_custom(self):
        self.assertEqual(self.config.folder_adm, 'ADMIN')

    def test_folder_op_custom(self):
        self.assertEqual(self.config.folder_op, '_PRODUCAO')

    def test_folder_op_phases_custom(self):
        self.assertEqual(self.config.folder_op_phases, ['VIAB', 'PROJ', 'OBRA'])

    def test_ignored_folders_includes_custom_functional(self):
        ignored = self.config.ignored_folders
        self.assertIn('_DOCS', ignored)
        self.assertIn('ADMIN', ignored)
        self.assertIn('_PRODUCAO', ignored)


if __name__ == '__main__':
    unittest.main()
