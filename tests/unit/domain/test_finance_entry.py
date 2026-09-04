import unittest
from foton_system.modules.clients.domain.models.finance_entry import FinanceEntry

class TestFinanceEntry(unittest.TestCase):
    def test_create_basic(self):
        entry = FinanceEntry(
            tipo="ENTRADA",
            valor=5000.0,
            descricao="Pagamento inicial",
            data="2026-06-01",
            cliente_alias="JOASILVA"
        )
        self.assertEqual(entry.tipo, "ENTRADA")
        self.assertEqual(entry.valor, 5000.0)
        self.assertEqual(entry.descricao, "Pagamento inicial")
        self.assertEqual(entry.data, "2026-06-01")
        self.assertEqual(entry.cliente_alias, "JOASILVA")

    def test_create_saida(self):
        entry = FinanceEntry(
            tipo="SAIDA",
            valor=1200.0,
            descricao="Impressao planta",
            data="2026-06-15",
            cliente_alias="MARIA"
        )
        self.assertEqual(entry.tipo, "SAIDA")
        self.assertEqual(entry.valor, 1200.0)

    def test_to_row(self):
        entry = FinanceEntry(
            tipo="ENTRADA",
            valor=5000.0,
            descricao="Pagamento inicial",
            data="2026-06-01",
            cliente_alias="JOASILVA",
            _id=1
        )
        row = entry.to_row()
        self.assertEqual(row["Tipo"], "ENTRADA")
        self.assertEqual(row["Valor"], 5000.0)
        self.assertEqual(row["Descricao"], "Pagamento inicial")
        self.assertEqual(row["Data"], "2026-06-01")
        self.assertEqual(row["Cliente"], "JOASILVA")
        self.assertEqual(row["ID"], 1)

    def test_from_row(self):
        row = {
            "ID": 1,
            "Tipo": "ENTRADA",
            "Valor": 5000.0,
            "Descricao": "Pagamento inicial",
            "Data": "2026-06-01",
            "Cliente": "JOASILVA",
        }
        entry = FinanceEntry.from_row(row)
        self.assertEqual(entry.tipo, "ENTRADA")
        self.assertEqual(entry.valor, 5000.0)
        self.assertEqual(entry.descricao, "Pagamento inicial")
        self.assertEqual(entry.data, "2026-06-01")
        self.assertEqual(entry.cliente_alias, "JOASILVA")
        self.assertEqual(entry._id, 1)

    def test_from_row_minimal(self):
        row = {
            "Tipo": "SAIDA",
            "Valor": 300.0,
            "Descricao": "Taxa",
            "Data": "2026-06-10",
            "Cliente": "MARIA",
        }
        entry = FinanceEntry.from_row(row)
        self.assertEqual(entry.tipo, "SAIDA")
        self.assertEqual(entry.valor, 300.0)
        self.assertIsNone(entry._id)

    def test_validate_invalid_tipo(self):
        with self.assertRaises(ValueError):
            FinanceEntry(
                tipo="INVALIDO",
                valor=100.0,
                descricao="Teste",
                data="2026-06-01",
                cliente_alias="TESTE"
            )

    def test_validate_negative_valor(self):
        with self.assertRaises(ValueError):
            FinanceEntry(
                tipo="ENTRADA",
                valor=-100.0,
                descricao="Teste",
                data="2026-06-01",
                cliente_alias="TESTE"
            )

    def test_validate_empty_descricao(self):
        with self.assertRaises(ValueError):
            FinanceEntry(
                tipo="ENTRADA",
                valor=100.0,
                descricao="",
                data="2026-06-01",
                cliente_alias="TESTE"
            )

    def test_validate_invalid_data_format(self):
        with self.assertRaises(ValueError):
            FinanceEntry(
                tipo="ENTRADA",
                valor=100.0,
                descricao="Teste",
                data="not-a-date",
                cliente_alias="TESTE"
            )

    def test_validate_empty_data(self):
        with self.assertRaises(ValueError):
            FinanceEntry(
                tipo="ENTRADA",
                valor=100.0,
                descricao="Teste",
                data="",
                cliente_alias="TESTE"
            )

    def test_validate_empty_cliente_alias(self):
        with self.assertRaises(ValueError):
            FinanceEntry(
                tipo="ENTRADA",
                valor=100.0,
                descricao="Teste",
                data="2026-06-01",
                cliente_alias=""
            )

if __name__ == "__main__":
    unittest.main()
