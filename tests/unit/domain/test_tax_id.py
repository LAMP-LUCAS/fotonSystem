import unittest
from foton_system.modules.clients.domain.value_objects import TaxId

class TestTaxId(unittest.TestCase):
    def test_valid_cpf_11_digits(self):
        tax = TaxId("12345678901")
        self.assertEqual(tax.clean, "12345678901")
    
    def test_valid_cnpj_14_digits(self):
        tax = TaxId("12345678000199")
        self.assertEqual(tax.clean, "12345678000199")
    
    def test_valid_with_formatting(self):
        tax = TaxId("123.456.789-01")
        self.assertEqual(tax.clean, "12345678901")
    
    def test_valid_nif_8_digits(self):
        tax = TaxId("12345678")
        self.assertEqual(tax.clean, "12345678")
    
    def test_invalid_too_short(self):
        with self.assertRaises(ValueError):
            TaxId("1234567")
    
    def test_invalid_too_long(self):
        with self.assertRaises(ValueError):
            TaxId("123456789012345")
    
    def test_invalid_empty(self):
        with self.assertRaises(ValueError):
            TaxId("")
    
    def test_invalid_special_chars_only(self):
        with self.assertRaises(ValueError):
            TaxId("...-///")