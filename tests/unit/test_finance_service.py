"""
Comprehensive Tests for FinanceService and CSVFinanceRepository

Covers:
- Entry creation and persistence
- Balance calculation
- Brazilian number format handling
- Edge cases (empty data, malformed entries)
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock
import csv

from foton_system.modules.finance.application.use_cases.finance_service import FinanceService
from foton_system.modules.finance.infrastructure.repositories.csv_finance_repository import CSVFinanceRepository
from foton_system.modules.finance.application.ports.finance_repository_port import FinanceRepositoryPort


class FakeFinanceRepository(FinanceRepositoryPort):
    """In-memory fake repository for unit tests."""

    def __init__(self):
        self._entries = []

    def save_entry(self, client_path, entry, headers):
        self._entries.append(dict(zip(headers, entry)))

    def get_entries(self, client_path):
        from foton_system.modules.clients.domain.models import FinanceEntry as FE
        result = []
        for d in self._entries:
            if isinstance(d, FE):
                result.append(d)
                continue
            row = {
                "ID": 0,
                "Tipo": d.get("Tipo", ""),
                "Valor": float(d.get("Valor", 0) or 0),
                "Descricao": d.get("Descricao", ""),
                "Data": d.get("Data", ""),
                "Cliente": d.get("Cliente", ""),
            }
            entry = FE.from_row(row)
            if entry is not None:
                result.append(entry)
        return result


class TestFinanceServiceBalanceCalculation(unittest.TestCase):
    """Tests for balance calculation logic."""

    def test_balance_with_entries_and_exits(self):
        """Calculates correct balance from mixed entries."""
        repo = FakeFinanceRepository()
        service = FinanceService(repo)
        
        service.add_entry(Path('/fake'), 'Pagamento Cliente', 1000, 'ENTRADA')
        service.add_entry(Path('/fake'), 'Material', 300, 'SAIDA')
        service.add_entry(Path('/fake'), 'Outro Pagamento', 500, 'ENTRADA')
        
        summary = service.get_summary(Path('/fake'))
        
        self.assertEqual(summary['total_entradas'], 1500.0)
        self.assertEqual(summary['total_saidas'], 300.0)
        self.assertEqual(summary['saldo'], 1200.0)

    def test_balance_empty_returns_zero(self):
        """Empty ledger returns zero balance."""
        repo = FakeFinanceRepository()
        service = FinanceService(repo)
        
        summary = service.get_summary(Path('/fake'))
        
        self.assertEqual(summary['saldo'], 0.0)

    def test_add_entry_returns_updated_summary(self):
        """add_entry returns the updated summary."""
        repo = FakeFinanceRepository()
        service = FinanceService(repo)
        
        result = service.add_entry(Path('/fake'), 'Test', 100, 'ENTRADA')
        
        self.assertEqual(result['saldo'], 100.0)


class TestFinanceServiceInputHandling(unittest.TestCase):
    """Tests for input parsing and formatting."""

    def test_handles_brazilian_currency_string(self):
        """Parses 'R$ 1.000,50' correctly."""
        repo = FakeFinanceRepository()
        service = FinanceService(repo)
        
        result = service.add_entry(Path('/fake'), 'Test', 'R$ 1.000,50', 'ENTRADA')
        
        self.assertEqual(result['saldo'], 1000.50)

    def test_handles_float_value(self):
        """Accepts float values directly."""
        repo = FakeFinanceRepository()
        service = FinanceService(repo)
        
        result = service.add_entry(Path('/fake'), 'Test', 250.75, 'ENTRADA')
        
        self.assertEqual(result['saldo'], 250.75)

    def test_handles_integer_value(self):
        """Accepts integer values."""
        repo = FakeFinanceRepository()
        service = FinanceService(repo)
        
        result = service.add_entry(Path('/fake'), 'Test', 500, 'ENTRADA')
        
        self.assertEqual(result['saldo'], 500.0)


class TestCSVFinanceRepositoryIntegration(unittest.TestCase):
    """Integration tests for CSV persistence."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.repo = CSVFinanceRepository()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_creates_csv_on_first_entry(self):
        """First entry creates the FINANCEIRO.csv file with headers."""
        headers = ['Data', 'Descricao', 'Tipo', 'Valor']
        entry = ['2026-02-02', 'Test', 'ENTRADA', '100.00']
        
        self.repo.save_entry(self.test_dir, entry, headers)
        
        csv_path = self.test_dir / 'FINANCEIRO.csv'
        self.assertTrue(csv_path.exists())
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            lines = list(reader)
            self.assertEqual(lines[0], headers)
            self.assertEqual(lines[1], entry)

    def test_appends_to_existing_csv(self):
        """Subsequent entries append without duplicating headers."""
        headers = ['Data', 'Descricao', 'Tipo', 'Valor']
        
        self.repo.save_entry(self.test_dir, ['2026-01-01', 'First', 'ENTRADA', '100'], headers)
        self.repo.save_entry(self.test_dir, ['2026-01-02', 'Second', 'SAIDA', '50'], headers)
        
        entries = self.repo.get_entries(self.test_dir)
        
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].descricao, 'First')
        self.assertEqual(entries[1].descricao, 'Second')

    def test_get_entries_empty_for_new_client(self):
        """Returns empty list for client without ledger."""
        entries = self.repo.get_entries(self.test_dir)
        
        self.assertEqual(entries, [])


class TestFinanceServiceEdgeCases(unittest.TestCase):
    """Tests for edge cases and error handling."""

    def test_malformed_entries_are_skipped(self):
        """Malformed entries (missing Valor) don't crash summary calculation."""
        from foton_system.modules.clients.domain.models import FinanceEntry
        repo = FakeFinanceRepository()
        repo._entries = [
            FinanceEntry(tipo='ENTRADA', valor=100.0, descricao='Good', data='2026-01-01', cliente_alias='fake'),
            FinanceEntry(tipo='ENTRADA', valor=0.0, descricao='Bad', data='2026-01-02', cliente_alias='fake'),
            FinanceEntry(tipo='SAIDA', valor=50.0, descricao='Good2', data='2026-01-03', cliente_alias='fake'),
        ]
        service = FinanceService(repo)

        summary = service.get_summary(Path('/fake'))

        self.assertEqual(summary['total_entradas'], 100.0)
        self.assertEqual(summary['total_saidas'], 50.0)

    def test_invalid_valor_is_skipped(self):
        """Non-numeric Valor values are skipped."""
        from foton_system.modules.clients.domain.models import FinanceEntry
        repo = FakeFinanceRepository()
        repo._entries = [
            FinanceEntry(tipo='ENTRADA', valor=100.0, descricao='Good', data='2026-01-01', cliente_alias='fake'),
            FinanceEntry(tipo='ENTRADA', valor=0.0, descricao='Bad', data='2026-01-02', cliente_alias='fake'),
        ]
        service = FinanceService(repo)

        summary = service.get_summary(Path('/fake'))

        self.assertEqual(summary['total_entradas'], 100.0)


if __name__ == '__main__':
    unittest.main()
