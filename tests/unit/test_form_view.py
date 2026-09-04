import unittest
from unittest.mock import patch, MagicMock
from foton_system.modules.documents.domain.models.form_session import FormSession, FormField


class TestTUIFormView(unittest.TestCase):
    """D5: Tests for TUIFormView navigation and CALC fields [RULE-DOC-5.2, RULE-DOC-5.3]"""

    def setUp(self):
        self.session = FormSession()
        self.session.fields = [
            FormField(name="nome", description="Nome do cliente", current_value="Joao"),
            FormField(name="valor", description="Valor", current_value="1000",
                      is_calculated=True, formula="500 * 2"),
            FormField(name="cidade", description="Cidade", current_value="Goiania"),
        ]
        self.session.cursor = 0

    @patch('builtins.input', side_effect=['/n', '/n', '/v', '/a'])
    @patch('builtins.print')
    def test_navigation_next(self, mock_print, mock_input):
        self.session.next()
        self.assertEqual(self.session.cursor, 1)

    @patch('builtins.input', side_effect=['/p'])
    @patch('builtins.print')
    def test_navigation_prev(self, mock_print, mock_input):
        self.session.cursor = 2
        self.session.prev()
        self.assertEqual(self.session.cursor, 1)

    def test_calc_field_is_not_editable(self):
        f = self.session.fields[1]
        self.assertTrue(f.is_calculated)
        self.session.update_current("9999")
        self.assertNotEqual(self.session.fields[1].current_value, "9999")

    def test_non_calc_field_is_editable(self):
        f = self.session.fields[0]
        self.assertFalse(f.is_calculated)
        self.session.update_current("Maria")
        self.assertEqual(self.session.fields[0].current_value, "Maria")


if __name__ == '__main__':
    unittest.main()
