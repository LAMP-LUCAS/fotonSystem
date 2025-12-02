import sys
import json
import re
from pathlib import Path
from colorama import init, Fore, Style
import pandas as pd

# Initialize colorama
init(autoreset=True)

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import ExcelClientRepository
from foton_system.scripts.fix_info_files import batch_fix

class SchemaManager:
    def __init__(self):
        self.config = Config()
        self.repository = ExcelClientRepository()
        self.schema_path = Path(__file__).resolve().parent.parent / 'config' / 'schema.json'
        self.schema = self._load_schema()
        
        # Discovery Data
        self.excel_columns = set()
        self.info_keys = set()
        self.all_system_variables = set()

    def _load_schema(self):
        if not self.schema_path.exists():
            return {"variables": {}}
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(Fore.RED + f"Erro ao carregar schema: {e}")
            return {"variables": {}}

    def _save_schema(self):
        try:
            with open(self.schema_path, 'w', encoding='utf-8') as f:
                json.dump(self.schema, f, indent=4, ensure_ascii=False)
            print(Fore.GREEN + "Schema salvo com sucesso!")
        except Exception as e:
            print(Fore.RED + f"Erro ao salvar schema: {e}")

    def discover_excel_variables(self):
        print(Fore.YELLOW + "Lendo colunas do Excel...")
        try:
            df = self.repository.get_clients_dataframe()
            self.excel_columns = set(df.columns)
        except Exception as e:
            print(Fore.RED + f"Erro ao ler Excel: {e}")

    def discover_info_variables(self):
        print(Fore.YELLOW + "Escaneando arquivos INFO...")
        # Scan a few latest files to get a superset of keys
        client_folders = self.repository.list_client_folders()
        
        count = 0
        max_scan = 10 # Scan 10 clients to be fast
        
        for client in client_folders:
            if count >= max_scan: break
            
            folder = self.repository.base_pasta / client
            # Find INFO-CLIENTE
            files = list(folder.glob(f"*_INFO-{client}.md"))
            if files:
                self._extract_keys(files[0])
                count += 1
                
    def _extract_keys(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if ':' in line:
                        key = line.split(':', 1)[0].strip()
                        if key.startswith('@'):
                            self.info_keys.add(key)
        except:
            pass

    def analyze(self):
        self.discover_excel_variables()
        self.discover_info_variables()
        
        self.all_system_variables = self.excel_columns.union(self.info_keys)
        
        registered = set(self.schema['variables'].keys())
        
        self.unregistered = self.all_system_variables - registered
        self.missing_in_system = registered - self.all_system_variables
        self.valid = registered.intersection(self.all_system_variables)

    def print_report(self):
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}{'RELATÓRIO DE GESTÃO DE VARIÁVEIS'.center(60)}")
        print(f"{Fore.CYAN}{'='*60}")
        
        print(f"\n{Fore.WHITE}Total de Variáveis no Sistema: {len(self.all_system_variables)}")
        print(f"{Fore.WHITE}Total Cadastradas no Schema: {len(self.schema['variables'])}")
        
        print(f"\n{Fore.GREEN}✔ VARIÁVEIS CADASTRADAS ({len(self.valid)})")
        # for v in sorted(self.valid):
        #     print(f"  - {v}")

        print(f"\n{Fore.YELLOW}⚠ NÃO CADASTRADAS (NOVAS) ({len(self.unregistered)})")
        for v in sorted(self.unregistered):
            origin = "Excel" if v in self.excel_columns else "InfoFile"
            if v in self.excel_columns and v in self.info_keys: origin = "Ambos"
            print(f"  - {v} ({origin})")

        if self.missing_in_system:
            print(f"\n{Fore.RED}✘ NO SCHEMA MAS NÃO NO SISTEMA ({len(self.missing_in_system)})")
            for v in sorted(self.missing_in_system):
                print(f"  - {v}")

    def add_variable(self, key):
        print(f"\nConfigurando variável: {Fore.CYAN}{key}")
        
        # Guess type and storage
        storage = "excel" if key in self.excel_columns else "info_file"
        if key in self.excel_columns and key in self.info_keys: storage = "ambos"
        
        desc = input(f"Descrição (Enter para pular): ")
        var_type = input(f"Tipo [string/int/float/date] (default: string): ") or "string"
        
        self.schema['variables'][key] = {
            "type": var_type,
            "storage": storage,
            "description": desc,
            "default": None
        }
        self._save_schema()

    def edit_variable(self, key):
        if key not in self.schema['variables']:
            print(Fore.RED + "Variável não encontrada no schema.")
            return

        curr = self.schema['variables'][key]
        print(f"\nEditando: {Fore.CYAN}{key}")
        print(f"Descrição Atual: {curr['description']}")
        print(f"Tipo Atual: {curr['type']}")
        
        new_desc = input(f"Nova Descrição (Enter para manter): ")
        new_type = input(f"Novo Tipo (Enter para manter): ")
        
        if new_desc: curr['description'] = new_desc
        if new_type: curr['type'] = new_type
        
        self._save_schema()

    def _update_info_files_regex(self, pattern, replacement):
        """Helper to replace text in all INFO files."""
        print(f"{Fore.YELLOW}>>> Atualizando arquivos INFO...")
        count = 0
        base_pasta = self.config.base_pasta_clientes
        
        for client_folder in base_pasta.iterdir():
            if not client_folder.is_dir() or client_folder.name in self.config.ignored_folders:
                continue
            
            # Recursive glob for all md files
            for file_path in client_folder.rglob("*.md"):
                if "INFO-" in file_path.name:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                        
                        if new_content != content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            count += 1
                    except Exception as e:
                        print(Fore.RED + f"Erro em {file_path.name}: {e}")
        print(Fore.GREEN + f"✔ {count} arquivos atualizados.")

    def rename_variable(self, old_key, new_key):
        if old_key not in self.schema['variables']:
            print(Fore.RED + "Variável original não encontrada no schema.")
            return
        
        print(f"\n{Fore.MAGENTA}=== RENOMEANDO VARIÁVEL ===")
        print(f"De: {old_key} -> Para: {new_key}")
        
        # 1. Update Schema
        self.schema['variables'][new_key] = self.schema['variables'].pop(old_key)
        self._save_schema()
        
        # 2. Update Excel
        if self.schema['variables'][new_key]['storage'] in ['excel', 'ambos']:
            print(f"{Fore.YELLOW}>>> Renomeando coluna no Excel...")
            try:
                df = self.repository.get_clients_dataframe()
                if old_key in df.columns:
                    df.rename(columns={old_key: new_key}, inplace=True)
                    self.repository.save_clients(df)
                    print(Fore.GREEN + "✔ Coluna renomeada.")
                else:
                    print(Fore.YELLOW + "⚠ Coluna original não encontrada no Excel.")
            except Exception as e:
                print(Fore.RED + f"Erro no Excel: {e}")

        # 3. Update Info Files
        if self.schema['variables'][new_key]['storage'] in ['info_file', 'ambos']:
            # Regex: Start of line, key, colon. 
            # Escape keys just in case they have special chars
            pattern = f"^{re.escape(old_key)}:"
            replacement = f"{new_key}:"
            self._update_info_files_regex(pattern, replacement)

    def merge_variables(self, source, target):
        if source not in self.schema['variables'] or target not in self.schema['variables']:
            print(Fore.RED + "Ambas as variáveis devem estar no schema.")
            return

        print(f"\n{Fore.MAGENTA}=== MESCLANDO VARIÁVEIS ===")
        print(f"Fonte (será apagada): {source}")
        print(f"Alvo (receberá dados): {target}")
        
        # 1. Update Excel
        if self.schema['variables'][target]['storage'] in ['excel', 'ambos']:
            print(f"{Fore.YELLOW}>>> Mesclando colunas no Excel...")
            try:
                df = self.repository.get_clients_dataframe()
                if source in df.columns and target in df.columns:
                    # Fill target with source where target is null
                    df[target] = df[target].fillna(df[source])
                    # Drop source
                    df.drop(columns=[source], inplace=True)
                    self.repository.save_clients(df)
                    print(Fore.GREEN + "✔ Dados mesclados e coluna fonte removida.")
                elif source in df.columns:
                    # Target doesn't exist in Excel yet? Rename source to target
                    print(Fore.YELLOW + "Alvo não existe no Excel. Renomeando fonte...")
                    df.rename(columns={source: target}, inplace=True)
                    self.repository.save_clients(df)
                else:
                    print(Fore.YELLOW + "⚠ Coluna fonte não encontrada no Excel.")
            except Exception as e:
                print(Fore.RED + f"Erro no Excel: {e}")

        # 2. Update Info Files
        if self.schema['variables'][target]['storage'] in ['info_file', 'ambos']:
            print(f"{Fore.YELLOW}>>> Mesclando chaves nos arquivos INFO...")
            # This is tricky via regex. We need to parse.
            # Strategy: 
            # If file has Source AND Target: Keep Target (maybe warn if data loss?), delete Source.
            # If file has Source ONLY: Rename Source to Target.
            # If file has Target ONLY: Do nothing.
            
            # We can reuse _update_info_files_regex for the Rename part (Source ONLY).
            # But for the "Both" case, we need logic.
            # Let's iterate manually.
            count = 0
            base_pasta = self.config.base_pasta_clientes
            for client_folder in base_pasta.iterdir():
                if not client_folder.is_dir() or client_folder.name in self.config.ignored_folders: continue
                for file_path in client_folder.rglob("*.md"):
                    if "INFO-" not in file_path.name: continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                        
                        new_lines = []
                        has_target = False
                        source_line = None
                        
                        # First pass: check existence
                        for line in lines:
                            if line.strip().startswith(f"{target}:"):
                                has_target = True
                                break
                        
                        # Second pass: build new content
                        modified = False
                        for line in lines:
                            if line.strip().startswith(f"{source}:"):
                                if has_target:
                                    # Skip source (delete it), target already exists
                                    modified = True
                                    continue 
                                else:
                                    # Rename source to target
                                    new_lines.append(line.replace(f"{source}:", f"{target}:", 1))
                                    modified = True
                            else:
                                new_lines.append(line)
                        
                        if modified:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.writelines(new_lines)
                            count += 1
                    except: pass
            print(Fore.GREEN + f"✔ {count} arquivos atualizados.")

        # 3. Update Schema
        del self.schema['variables'][source]
        self._save_schema()
        print(Fore.GREEN + "✔ Variável fonte removida do Schema.")

    def sync_system(self):
        print(f"\n{Fore.MAGENTA}=== INICIANDO SINCRONIZAÇÃO ===")
        
        # 1. Sync Excel
        print(f"\n{Fore.YELLOW}>>> Sincronizando Excel...")
        excel_vars = [k for k, v in self.schema['variables'].items() if v['storage'] in ['excel', 'ambos']]
        
        try:
            df = self.repository.get_clients_dataframe()
            changed = False
            for var in excel_vars:
                if var not in df.columns:
                    print(f"  + Criando coluna: {var}")
                    df[var] = None # Create empty column
                    changed = True
            
            if changed:
                self.repository.save_clients(df)
                print(Fore.GREEN + "✔ Excel atualizado com sucesso.")
            else:
                print(Fore.GREEN + "✔ Excel já está sincronizado.")
        except Exception as e:
            print(Fore.RED + f"Erro ao sincronizar Excel: {e}")

        # 2. Sync Info Files
        print(f"\n{Fore.YELLOW}>>> Sincronizando Arquivos INFO...")
        info_vars = [k for k, v in self.schema['variables'].items() if v['storage'] in ['info_file', 'ambos']]
        batch_fix(client_keys=info_vars, service_keys=info_vars)


    def menu(self):
        while True:
            self.analyze()
            self.print_report()
            
            print(f"\n{Fore.CYAN}OPÇÕES:")
            print("1. Adicionar TODAS as não cadastradas (Automático)")
            print("2. Adicionar variável específica")
            print("3. Editar variável (Descrição/Tipo)")
            print("4. Renomear variável (Refatorar)")
            print("5. Mesclar variáveis (Merge)")
            print("6. SINCRONIZAR SISTEMA (Schema -> Excel/Arquivos)")
            print("7. Sair")
            
            choice = input("\nEscolha: ")
            
            if choice == '1':
                for var in self.unregistered:
                    self.schema['variables'][var] = {
                        "type": "string",
                        "storage": "excel" if var in self.excel_columns else "info_file",
                        "description": "Importado automaticamente",
                        "default": None
                    }
                self._save_schema()
            elif choice == '2':
                key = input("Digite o nome da variável: ")
                self.add_variable(key)
            elif choice == '3':
                key = input("Nome da variável para editar: ")
                self.edit_variable(key)
            elif choice == '4':
                old = input("Nome ATUAL: ")
                new = input("Nome NOVO: ")
                confirm = input(f"Isso vai alterar arquivos e banco de dados. Confirmar {old}->{new}? (s/n): ")
                if confirm.lower() == 's': self.rename_variable(old, new)
            elif choice == '5':
                src = input("Variável FONTE (será apagada): ")
                tgt = input("Variável ALVO (será mantida): ")
                confirm = input(f"Isso vai apagar {src} e mover dados para {tgt}. Confirmar? (s/n): ")
                if confirm.lower() == 's': self.merge_variables(src, tgt)
            elif choice == '6':
                confirm = input("Isso vai alterar o Excel e arquivos. Tem certeza? (s/n): ")
                if confirm.lower() == 's':
                    self.sync_system()
            elif choice == '7':
                break


__title__ = "Gestão de Variáveis (Schema Manager)"

def main():
    manager = SchemaManager()
    if "--report" in sys.argv:
        manager.analyze()
        manager.print_report()
    elif "--sync" in sys.argv:
        manager.analyze()
        manager.sync_system()
    else:
        manager.menu()

if __name__ == "__main__":
    main()
