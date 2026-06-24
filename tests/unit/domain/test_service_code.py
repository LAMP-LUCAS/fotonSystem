import unittest
from foton_system.modules.clients.domain.value_objects import ServiceCode

class TestServiceCode(unittest.TestCase):
    def test_valid_code(self):
        code = ServiceCode("JOSRES01")
        self.assertEqual(str(code), "JOSRES01")
    
    def test_valid_code_lowercase(self):
        code = ServiceCode("josres01")
        self.assertEqual(str(code), "JOSRES01")
    
    def test_invalid_code_too_short(self):
        with self.assertRaises(ValueError):
            ServiceCode("JOSRES1")
    
    def test_invalid_code_too_long(self):
        with self.assertRaises(ValueError):
            ServiceCode("JOSRES001")
    
    def test_invalid_code_no_digits(self):
        with self.assertRaises(ValueError):
            ServiceCode("JOSRES")
    
    def test_invalid_code_special_chars(self):
        with self.assertRaises(ValueError):
            ServiceCode("JOS-RES01")