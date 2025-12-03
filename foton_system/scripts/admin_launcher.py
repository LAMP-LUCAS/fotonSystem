import sys
import importlib.util
from pathlib import Path
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Determine scripts directory
if getattr(sys, 'frozen', False):
    SCRIPTS_DIR = Path(sys._MEIPASS) / "foton_system" / "scripts"
else:
    # Assuming running from project root
    SCRIPTS_DIR = Path("foton_system/scripts")

def load_scripts():
    """Scans the scripts directory and returns a list of executable modules."""
    scripts = []
    if not SCRIPTS_DIR.exists():
        print(Fore.RED + f"Diretório de scripts não encontrado: {SCRIPTS_DIR}")
        return []

    for file_path in SCRIPTS_DIR.glob("*.py"):
        if file_path.name.startswith("__") or file_path.name.startswith("test_"):
            continue
            
        try:
            # Import module dynamically
            spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check for metadata and main function
            if hasattr(module, "__title__") and hasattr(module, "main"):
                scripts.append({
                    "title": module.__title__,
                    "module": module,
                    "filename": file_path.name
                })
        except Exception as e:
            # print(Fore.RED + f"Erro ao carregar {file_path.name}: {e}")
            pass
            
    return sorted(scripts, key=lambda x: x["title"])

def main_menu():
    scripts = load_scripts()
    
    while True:
        print(f"\n{Fore.CYAN}{'='*40}")
        print(f"{Fore.CYAN}{'FERRAMENTAS ADMINISTRATIVAS'.center(40)}")
        print(f"{Fore.CYAN}{'='*40}")
        
        for i, script in enumerate(scripts, 1):
            print(f"{Fore.WHITE}{i}. {script['title']}")
        
        print(f"{Fore.WHITE}0. Voltar")
        print(f"{Fore.CYAN}{'='*40}")
        
        choice = input(f"\n{Fore.YELLOW}Escolha uma opção: {Style.RESET_ALL}")
        
        try:
            idx = int(choice)
            if idx == 0:
                print(Fore.CYAN + "Voltando...")
                return # Return to caller instead of exit
            elif 0 <= idx < len(scripts):
                selected = scripts[idx]
                print(f"\n{Fore.GREEN}>>> Iniciando: {selected['title']}...\n")
                try:
                    selected["module"].main()
                except Exception as e:
                    print(Fore.RED + f"Erro na execução: {e}")
                
                input(f"\n{Fore.YELLOW}Pressione Enter para voltar ao menu...{Style.RESET_ALL}")
            else:
                print(Fore.RED + "Opção inválida.")
        except ValueError:
            print(Fore.RED + "Por favor, digite um número.")

if __name__ == "__main__":
    main_menu()
