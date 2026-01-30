import unittest
import shutil
import tempfile
from pathlib import Path
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
