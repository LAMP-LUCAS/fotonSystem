import unittest
from unittest.mock import MagicMock, patch
from foton_system.interfaces.cli.menus import MenuSystem

class TestMenuUI(unittest.TestCase):
    def setUp(self):
        # Patching dependencies to avoid real IDO/DB access
        with patch('foton_system.modules.clients.infrastructure.repositories.excel_client_repository.ExcelClientRepository'), \
             patch('foton_system.modules.documents.infrastructure.adapters.python_docx_adapter.PythonDocxAdapter'), \
             patch('foton_system.modules.documents.infrastructure.adapters.python_pptx_adapter.PythonPPTXAdapter'):
            self.menu = MenuSystem()

    def test_main_menu_display(self):
        """Valida se o menu principal contém as opções esperadas."""
        with patch('builtins.input', return_value='0'), \
             patch('builtins.print') as mock_print:
            with self.assertRaises(SystemExit):
                self.menu.run()
            
            # Verifica se as opções principais estão sendo impressas
            printed_content = "".join([call.args[0] for call in mock_print.call_args_list if call.args])
            self.assertIn("Gerenciar Clientes", printed_content)
            self.assertIn("Gerenciar Serviços", printed_content)
            self.assertIn("Documentos", printed_content)
            self.assertIn("Produtividade", printed_content)
            self.assertIn("Configurações", printed_content)
            self.assertIn("Sair", printed_content)

    def test_navigation_to_clients(self):
        """Valida a navegação para o menu de clientes."""
        # Mock inputs: 1 (Clientes), 0 (Voltar), 0 (Sair)
        with patch('builtins.input', side_effect=['1', '0', '0']), \
             patch('builtins.print') as mock_print:
            with self.assertRaises(SystemExit):
                self.menu.run()
            
            printed_content = "".join([call.args[0] for call in mock_print.call_args_list if call.args])
            self.assertIn("Gerenciar Clientes", printed_content)
            self.assertIn("Sincronizar Base", printed_content)

    def test_navigation_to_settings(self):
        """Valida a navegação para o menu de configurações."""
        # Mock inputs: 5 (Configurações), 0 (Voltar), 0 (Sair)
        with patch('builtins.input', side_effect=['5', '0', '0']), \
             patch('builtins.print') as mock_print:
            with self.assertRaises(SystemExit):
                self.menu.run()
            
            printed_content = "".join([call.args[0] for call in mock_print.call_args_list if call.args])
            self.assertIn("Configurações", printed_content)
            self.assertIn("Pasta de Clientes", printed_content)

if __name__ == '__main__':
    unittest.main()
