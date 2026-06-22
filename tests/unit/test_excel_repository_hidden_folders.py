"""Tests: ExcelClientRepository filtra pastas ocultas (FASE A)."""
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestListClientFoldersFiltersHiddenDirs(unittest.TestCase):
    """list_client_folders() deve ignorar pastas iniciadas por '.'."""

    def setUp(self):
        self.temp_dir = Path(__file__).parent / "_test_hidden_folders"
        self.temp_dir.mkdir(exist_ok=True)
        for p in self.temp_dir.iterdir():
            if p.is_dir():
                import shutil
                shutil.rmtree(p)
            else:
                p.unlink()

        # Cria pastas visíveis
        (self.temp_dir / "CLIENTE_A").mkdir()
        (self.temp_dir / "CLIENTE_B").mkdir()
        # Cria pastas ocultas
        (self.temp_dir / ".git").mkdir()
        (self.temp_dir / ".obsidian").mkdir()

    def tearDown(self):
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_list_client_folders_excludes_dot_dirs(self):
        """Pastas com '.' inicial não devem aparecer no resultado."""
        cfg = MagicMock()
        cfg.base_pasta_clientes = self.temp_dir
        cfg.base_dados = self.temp_dir / "baseDados.xlsx"

        from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import (
            ExcelClientRepository,
        )
        repo = ExcelClientRepository(config=cfg)
        folders = repo.list_client_folders()

        self.assertNotIn(".git", folders)
        self.assertNotIn(".obsidian", folders)
        self.assertIn("CLIENTE_A", folders)
        self.assertIn("CLIENTE_B", folders)


class TestSyncServiceFiltersHiddenDirs(unittest.TestCase):
    """sync_dashboard() deve ignorar pastas ocultas."""

    def setUp(self):
        self.temp_dir = Path(__file__).parent / "_test_sync_hidden"
        self.temp_dir.mkdir(exist_ok=True)
        for p in self.temp_dir.iterdir():
            if p.is_dir():
                import shutil
                shutil.rmtree(p)
            else:
                p.unlink()

        (self.temp_dir / "CLIENTE_OK").mkdir()
        (self.temp_dir / ".git").mkdir()
        (self.temp_dir / ".obsidian").mkdir()

    def tearDown(self):
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @patch("foton_system.modules.sync.sync_service.Config")
    def test_sync_ignores_dot_folders(self, MockConfig):
        """sync_dashboard não deve processar pastas ocultas."""
        cfg = MagicMock()
        cfg.base_pasta_clientes = self.temp_dir
        cfg.base_dados = self.temp_dir / "baseDados.xlsx"
        MockConfig.return_value = cfg

        from foton_system.modules.sync.sync_service import SyncService
        svc = SyncService()
        # Se tentasse processar .git, falharia ao tentar ler INFO file
        result = svc.sync_dashboard()
        self.assertEqual(result, 0, "Nenhum cliente válido encontrado (pastas ocultas ignoradas)")


if __name__ == "__main__":
    unittest.main()
