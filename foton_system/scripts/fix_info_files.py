import os
import re
from pathlib import Path
import sys
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Import Config
try:
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
    from foton_system.modules.shared.infrastructure.config.config import Config
    config = Config()
except ImportError:
    print(Fore.RED + "Erro: Configuração não encontrada.")
    sys.exit(1)

# Handle path for both dev and frozen (PyInstaller) modes
if getattr(sys, 'frozen', False):
    base_path = Path(sys._MEIPASS) / "foton_system"
else:
    base_path = Path(__file__).resolve().parent.parent

TEMPLATE_PATH = base_path / "assets" / "info-Template.md"

def parse_template(path):
    """Parses the template file to extract keys for Client and Service."""
    client_keys = []
    service_keys = []
    
    current_section = None
    
    if not path.exists():
        print(Fore.RED + f"Template não encontrado: {path}")
        return [], []

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if "## INFO-CLIENTE.md" in line:
                current_section = "CLIENT"
            elif "## INFO-SERVICO.md" in line:
                current_section = "SERVICE"
            
            if line.startswith("@"):
                # Extract key (first word starting with @)
                match = re.match(r"^(@[\w%]+)", line)
                if match:
                    key = match.group(1)
                    # Use the whole line as comment/description if needed, 
                    # but for now we just want the key to ensure it exists.
                    # We will append "Key: " to the file.
                    if current_section == "CLIENT":
                        client_keys.append(key)
                    elif current_section == "SERVICE":
                        service_keys.append(key)
    
    return client_keys, service_keys

def get_latest_info_file(folder, alias, suffix):
    files = list(folder.glob(f"*_INFO-{alias}.md"))
    if not files:
        return None
    files.sort(key=lambda f: f.name, reverse=True)
    return files[0]

def fix_file(path, required_keys):
    """Appends missing keys to the file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        existing_keys = set()
        for line in lines:
            if ':' in line:
                k = line.split(':', 1)[0].strip()
                existing_keys.add(k)
        
        missing = [k for k in required_keys if k not in existing_keys]
        
        if not missing:
            return False # No changes
        
        with open(path, 'a', encoding='utf-8') as f:
            f.write("\n\n### VARIÁVEIS ADICIONADAS AUTOMATICAMENTE\n")
            for k in missing:
                f.write(f"{k}: \n")
        
        return True
    except Exception as e:
        print(Fore.RED + f"Erro ao corrigir {path}: {e}")
        return False

def batch_fix(client_keys=None, service_keys=None):
    """
    Runs the batch fix process.
    If keys are provided, uses them. Otherwise, parses the template.
    """
    print(Fore.CYAN + "=== CORREÇÃO EM LOTE DE ARQUIVOS INFO ===")
    
    if client_keys is None or service_keys is None:
        c_keys, s_keys = parse_template(TEMPLATE_PATH)
        if client_keys is None: client_keys = c_keys
        if service_keys is None: service_keys = s_keys
        print(f"Template carregado. Chaves Cliente: {len(client_keys)}, Chaves Serviço: {len(service_keys)}")
    else:
        print(f"Usando chaves fornecidas. Cliente: {len(client_keys)}, Serviço: {len(service_keys)}")
    
    base_pasta = config.base_pasta_clientes
    
    # Process Clients
    print(Fore.YELLOW + "\n>>> Processando Clientes...")
    for client_folder in base_pasta.iterdir():
        if not client_folder.is_dir() or client_folder.name in config.ignored_folders:
            continue
            
        alias = client_folder.name
        info_file = get_latest_info_file(client_folder, alias, "CLIENTE")
        
        if info_file:
            if fix_file(info_file, client_keys):
                print(Fore.GREEN + f"✔ {alias}: Atualizado.")
            else:
                pass
        else:
            print(Fore.RED + f"✘ {alias}: Arquivo INFO não encontrado.")

        # Process Services
        for service_folder in client_folder.iterdir():
            if not service_folder.is_dir():
                continue
                
            service_alias = service_folder.name
            info_service = get_latest_info_file(service_folder, service_alias, "SERVICO")
            
            if info_service:
                if fix_file(info_service, service_keys):
                    print(Fore.GREEN + f"✔ {alias}/{service_alias}: Atualizado.")
                else:
                    pass
            else:
                pass

    print(Fore.CYAN + "\n=== CONCLUÍDO ===")


__title__ = "Correção em Lote (Info Files)"

def main():
    batch_fix()

if __name__ == "__main__":
    main()
