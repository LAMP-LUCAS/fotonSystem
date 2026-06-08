import unittest
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock
from foton_system.modules.finance.application.use_cases.finance_service import FinanceService
from foton_system.modules.finance.infrastructure.repositories.csv_finance_repository import CSVFinanceRepository

class TestFinanceService(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.repo = CSVFinanceRepository()
        self.service = FinanceService(self.repo)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_add_entry_creates_file(self):
        summary = self.service.add_entry(self.test_dir, "Test Payment", 100.00, "ENTRADA")
        self.assertTrue((self.test_dir / "FINANCEIRO.csv").exists())
        self.assertEqual(summary['saldo'], 100.00)

    def test_calculate_balance(self):
        self.service.add_entry(self.test_dir, "In", 200, "ENTRADA")
        self.service.add_entry(self.test_dir, "Out", 50, "SAIDA")
        summary = self.service.get_summary(self.test_dir)
        self.assertEqual(summary['saldo'], 150.00)
        self.assertEqual(summary['total_entradas'], 200.00)
        self.assertEqual(summary['total_saidas'], 50.00)

if __name__ == '__main__':
    unittest.main()


class TestCSVFinanceRepositoryLedgerPath(unittest.TestCase):
    """Tests for CSVFinanceRepository._get_ledger_path fallback logic."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_new_path_used_when_no_existing_file(self):
        """When neither file exists, new_path ({ADM}/FINANCEIRO.csv) should be returned."""
        mock_config = MagicMock()
        type(mock_config).folder_adm = PropertyMock(return_value='01_ADM')
        repo = CSVFinanceRepository(config=mock_config)
        result = repo._get_ledger_path(self.test_dir)
        self.assertEqual(result, self.test_dir / '01_ADM' / 'FINANCEIRO.csv')

    def test_new_path_used_when_it_exists(self):
        """When {ADM}/FINANCEIRO.csv exists, it should be returned."""
        adm = self.test_dir / '01_ADM'
        adm.mkdir()
        (adm / 'FINANCEIRO.csv').write_text('data', encoding='utf-8')
        mock_config = MagicMock()
        type(mock_config).folder_adm = PropertyMock(return_value='01_ADM')
        repo = CSVFinanceRepository(config=mock_config)
        result = repo._get_ledger_path(self.test_dir)
        self.assertEqual(result, adm / 'FINANCEIRO.csv')

    def test_legacy_path_used_when_only_root_file_exists(self):
        """When only root FINANCEIRO.csv exists, it should be returned (fallback)."""
        (self.test_dir / 'FINANCEIRO.csv').write_text('data', encoding='utf-8')
        mock_config = MagicMock()
        type(mock_config).folder_adm = PropertyMock(return_value='01_ADM')
        repo = CSVFinanceRepository(config=mock_config)
        result = repo._get_ledger_path(self.test_dir)
        self.assertEqual(result, self.test_dir / 'FINANCEIRO.csv')

    def test_no_config_returns_root_path(self):
        """When no config is provided, root FINANCEIRO.csv should be returned."""
        repo = CSVFinanceRepository()
        result = repo._get_ledger_path(self.test_dir)
        self.assertEqual(result, self.test_dir / 'FINANCEIRO.csv')
