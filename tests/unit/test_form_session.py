import unittest
from unittest.mock import patch, MagicMock
from foton_system.modules.documents.domain.models.form_session import FormSession
from foton_system.interfaces.cli.views.form_view import TUIFormView

class TestTUIFormFiller(unittest.TestCase):
    """
    Unit tests for TUI Form Interaction Logic.
    Uses mocks to simulate user input.
    """

    def setUp(self):
        self.session = FormSession()
        self.md_content = """# TEST
@nome; João
@valor; 1000
@total; [calculo: @valor * 2] Resultado
"""
        self.session.parse_markdown(self.md_content)
        self.view = TUIFormView(self.session)

    @patch('builtins.input')
    @patch('os.system')
    def test_navigation_and_edit_cycle(self, mock_os, mock_input):
        """
        Simulates: Change name -> Next -> Change value -> Prev -> Save.
        """
        # Command Sequence:
        # 1. "Maria" (Update @nome, moves to next)
        # 2. "2000" (Update @valor, moves to next)
        # 3. "p" (Move back to @valor)
        # 4. "s" (Save)
        # 5. "s" (Confirm save)
        mock_input.side_effect = ["Maria", "2000", "p", "s", "s"]

        action = self.view.run_loop()

        # Check final state
        self.assertEqual(action, "save")
        
        # Verify field updates
        fields = {f.name: f for f in self.session.fields}
        self.assertEqual(fields['nome'].current_value, "Maria")
        self.assertEqual(fields['valor'].current_value, "2000")
        
        # Verify calculation was triggered (Mocking FormSession logic if needed, but it should work)
        # Note: FormSession might need manual trigger if not in real loop, 
        # but here the view calls update_current which triggers re-calc.
        self.assertEqual(fields['total'].current_value, "4000.00")

    @patch('builtins.input')
    @patch('os.system')
    def test_cancel_action(self, mock_os, mock_input):
        """
        Simulates: Change something -> Cancel -> Confirm Cancel.
        """
        mock_input.side_effect = ["New Name", "c", "s"]
        action = self.view.run_loop()
        self.assertEqual(action, "cancel")

if __name__ == '__main__':
    unittest.main()
