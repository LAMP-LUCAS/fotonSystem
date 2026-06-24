import unittest
from foton_system.modules.clients.domain.value_objects import ClientCode

class TestClientCode(unittest.TestCase):
    def test_valid_code(self):
        code = ClientCode("JOS01")
        self.assertEqual(str(code), "JOS01")
    
    def test_valid_code_lowercase(self):
        code = ClientCode("jos01")
        self.assertEqual(str(code), "JOS01")
    
    def test_invalid_code_too_short(self):
        with self.assertRaises(ValueError):
            ClientCode("JOS1")
    
    def test_invalid_code_too_long(self):
        with self.assertRaises(ValueError):
            ClientCode("JOSEPH01")
    
    def test_invalid_code_no_digits(self):
        with self.assertRaises(ValueError):
            ClientCode("JOSEPH")
    
    def test_invalid_code_special_chars(self):
        with self.assertRaises(ValueError):
            ClientCode("JOS-01")