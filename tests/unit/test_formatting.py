import unittest
from datetime import datetime
from foton_system.modules.shared.infrastructure.utils.formatting import FotonFormatter

class TestFotonFormatter(unittest.TestCase):
    def test_currency_formatting(self):
        self.assertEqual(FotonFormatter.format_currency(1000), "R$ 1.000,00")
        self.assertEqual(FotonFormatter.format_currency(1000.50), "R$ 1.000,50")
        self.assertEqual(FotonFormatter.format_currency("5000.00"), "R$ 5.000,00")
        self.assertEqual(FotonFormatter.format_currency("R$ 1000"), "R$ 1.000,00")

    def test_decimal_formatting(self):
        self.assertEqual(FotonFormatter.format_decimal(1234.56), "1.234,56")
        self.assertEqual(FotonFormatter.format_decimal(140), "140,00")

    def test_parse_br_number(self):
        self.assertEqual(FotonFormatter.parse_br_number("1.234,56"), 1234.56)
        self.assertEqual(FotonFormatter.parse_br_number("R$ 5.000,00"), 5000.00)
        self.assertEqual(FotonFormatter.parse_br_number("1000"), 1000.0)

    def test_date_formatting(self):
        dt = datetime(2026, 1, 29)
        self.assertEqual(FotonFormatter.get_full_date(dt), "29 de Janeiro de 2026")

if __name__ == '__main__':
    unittest.main()
