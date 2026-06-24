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
        # 3. "/p" (Move back to @valor)
        # 4. "/s" (Save)
        # 5. "S" (Confirm save)
        mock_input.side_effect = ["Maria", "2000", "/p", "/s", "S"]

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
        mock_input.side_effect = ["New Name", "/c", "S"]
        action = self.view.run_loop()
        self.assertEqual(action, "cancel")

    @patch('builtins.input')
    @patch('os.system')
    def test_save_confirmed_with_uppercase_S(self, mock_os, mock_input):
        """
        Save command + uppercase 'S' confirmation -> "save".
        Ensures .upper() != 'S' accepts uppercase S.
        """
        mock_input.side_effect = ["/s", "S"]
        action = self.view.run_loop()
        self.assertEqual(action, "save")

    @patch('builtins.input')
    @patch('os.system')
    def test_save_cancelled_with_N_then_confirmed(self, mock_os, mock_input):
        """
        Save command + 'N' cancels (stays in loop),
        then save + 'S' confirms.
        """
        mock_input.side_effect = ["/s", "N", "/s", "S"]
        action = self.view.run_loop()
        self.assertEqual(action, "save")

    @patch('builtins.input')
    @patch('os.system')
    def test_cancel_cancelled_with_any_key(self, mock_os, mock_input):
        """
        Cancel command + 'x' cancels the exit (stays in loop),
        then save + 'S' confirms.
        Ensures ANY key != 'S' cancels the confirmation.
        """
        mock_input.side_effect = ["/c", "x", "/s", "S"]
        action = self.view.run_loop()
        self.assertEqual(action, "save")

    @patch('builtins.input')
    @patch('os.system')
    def test_raw_value_over_old_command(self, mock_os, mock_input):
        """
        Typing 'n' (an old command) sets it as value instead of navigating.
        Then '/s' save to confirm.
        Ensures RULE-UX-6.2: commands without '/' are treated as literal values.
        """
        mock_input.side_effect = ["n", "/s", "S"]
        action = self.view.run_loop()
        self.assertEqual(action, "save")
        fields = {f.name: f for f in self.session.fields}
        self.assertEqual(fields['nome'].current_value, "n")

    @patch('builtins.input')
    @patch('os.system')
    def test_slash_n_navigates_next(self, mock_os, mock_input):
        """
        '/n' navigates to next field, skipping field edit.
        Then '/p' goes back, then '/s' saves.
        """
        mock_input.side_effect = ["/n", "/p", "/s", "S"]
        action = self.view.run_loop()
        self.assertEqual(action, "save")

    @patch('builtins.input')
    @patch('os.system')
    def test_value_conflicts_with_old_command_p(self, mock_os, mock_input):
        """
        Typing 'p' sets it as value literal (not 'prev').
        Then '/p' goes back to see it was set.
        Ensures old single-letter commands are no longer interpreted.
        """
        mock_input.side_effect = ["p", "/p", "/s", "S"]
        action = self.view.run_loop()
        self.assertEqual(action, "save")
        fields = {f.name: f for f in self.session.fields}
        self.assertEqual(fields['nome'].current_value, "p")

    @patch('builtins.input')
    @patch('os.system')
    def test_slash_a_save_as(self, mock_os, mock_input):
        """
        '/a' triggers 'save_as' action directly (no confirmation prompt).
        """
        mock_input.side_effect = ["/a"]
        action = self.view.run_loop()
        self.assertEqual(action, "save_as")

    @patch('builtins.input')
    @patch('os.system')
    def test_empty_entered_advances_to_next(self, mock_os, mock_input):
        """
        Empty input (just Enter) advances to next field.
        Then '/s' saves.
        """
        mock_input.side_effect = ["", "/s", "S"]
        action = self.view.run_loop()
        self.assertEqual(action, "save")

if __name__ == '__main__':
    unittest.main()
