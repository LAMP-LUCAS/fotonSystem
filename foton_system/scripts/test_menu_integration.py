import sys
from pathlib import Path
from unittest.mock import patch

# Add project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from foton_system.interfaces.cli.menus import MenuSystem

def test_integration():
    print("=== TESTANDO INTEGRAÇÃO DO MENU ===")
    
    # Mock inputs to navigate: 
    # 5 (Configurações) -> 4 (Ferramentas Admin) -> 4 (Voltar do Admin) -> 0 (Voltar Config) -> 0 (Sair Main)
    inputs = ['5', '4', '4', '0', '0']
    
    with patch('builtins.input', side_effect=inputs):
        try:
            menu = MenuSystem()
            menu.run()
            print("\n✔ Navegação concluída com sucesso (Sair -> 0).")
        except SystemExit:
            print("\n✔ Sistema encerrou corretamente.")
        except Exception as e:
            print(f"\n✘ Erro na navegação: {e}")

if __name__ == "__main__":
    test_integration()
