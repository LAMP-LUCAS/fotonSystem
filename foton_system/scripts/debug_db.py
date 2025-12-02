import pandas as pd
from pathlib import Path
import sys
import re
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Import Config and Repository
try:
    # Add project root to path (3 levels up: scripts -> foton_system -> lamp)
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
    from foton_system.modules.shared.infrastructure.config.config import Config
    from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import ExcelClientRepository
    config = Config()
except ImportError as e:
    print(Fore.RED + f"Erro: Não foi possível importar módulos do sistema: {e}")
    print(Fore.YELLOW + "Certifique-se de estar rodando o script da raiz do projeto ou da pasta scripts.")
    sys.exit(1)

# Expected Keys based on User Template
EXPECTED_CLIENT_KEYS = {
    '@dataProposta', '@numeroProposta', '@nomeProposta', '@cidadeProposta', 
    '@localProposta', '@geolocalizacaoProposta', '@nomeCliente', '@empregoCliente', 
    '@estadoCivilCliente', '@cpfCnpjCliente', '@enderecoCliente'
}

EXPECTED_SERVICE_KEYS = {
    '@TEMPLATE', '@DataAtual', 
    # Client Contract Data
    '@nomeContrato', '@numeroContrato', '@nomeClienteContrato', 
    '@estadoCivilClienteContrato', '@empregoClienteContrato', '@telefoneClienteContrato', 
    '@emailClienteContrato', '@enderecoClienteContrato', '@cpfCnpjClienteContrato',
    # Service Data
    '@modalidadeServico', '@anoProjeto', '@demandaProposta', '@areaTotal', 
    '@areaCoberta', '@areaDescoberta', '@detalhesProposta', '@estiloProjeto', 
    '@ambientesProjeto', '@inProposta', '@lvProposta', '@anProposta', 
    '@baProposta', '@prProposta', '@inSolucao', '@valorProposta', '@valorContrato',
    # Cost Estimation
    '@projArqEng', '@procLegais', '@ACEqv', '@execcub', '@execInfra', 
    '@execPais', '@execMob', '@totalParcial', '@totalExec', '@totalinss', 
    '@totalGeral', '@ArqEng%', '@Legais%', '@precoCUB%', '@Parcial%', 
    '@infra%', '@pais%', '@mob%', '@Exec%', '@inss%'
}

class DatabaseDebugger:
    def __init__(self):
        self.repository = ExcelClientRepository()
        self.base_pasta_clientes = config.base_pasta_clientes
        self.df_clients = None
        self.df_services = None
        
        # Logging setup
        self.log_buffer = []
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)

    def log(self, message, color=Fore.WHITE, style=Style.NORMAL):
        """Prints to console with color and buffers clean text for report."""
        # Print to console
        print(f"{style}{color}{message}{Style.RESET_ALL}")
        
        # Clean ANSI codes for file
        clean_message = re.sub(r'\x1b\[[0-9;]*m', '', message)
        self.log_buffer.append(clean_message)

    def print_header(self, title):
        sep = '='*60
        self.log(f"\n{sep}", Fore.CYAN)
        self.log(f"{title.center(60)}", Fore.CYAN)
        self.log(f"{sep}", Fore.CYAN)

    def print_sub_header(self, title):
        self.log(f"\n>>> {title}", Fore.YELLOW)

    def save_report(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = self.reports_dir / f"debug_report_{timestamp}.md"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(self.log_buffer))
            print(f"\n{Fore.CYAN}Relatório salvo em: {filename}{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}Erro ao salvar relatório: {e}{Style.RESET_ALL}")

    def check_files(self):
        self.print_header("VERIFICAÇÃO DE ARQUIVOS")
        
        # We can use repository check_files, but it raises exception.
        # Let's wrap it or check manually using repository paths if exposed.
        # Repository exposes base_dados and base_pasta (initialized from config).
        
        files = [
            ("Base de Dados (Excel)", self.repository.base_dados),
            ("Pasta de Clientes", self.repository.base_pasta)
        ]

        all_ok = True
        for name, path in files:
            if path.exists():
                self.log(f"✔ {name}: Encontrado em {path}", Fore.GREEN)
            else:
                self.log(f"✘ {name}: NÃO ENCONTRADO em {path}", Fore.RED)
                all_ok = False
        
        return all_ok

    def analyze_clients(self):
        self.print_header("ANÁLISE DE CLIENTES")
        
        try:
            self.df_clients = self.repository.get_clients_dataframe()
        except Exception as e:
            self.log(f"Erro ao ler aba 'baseClientes' via Repositório: {e}", Fore.RED)
            return

        # Basic Stats
        total = len(self.df_clients)
        self.log(f"Total de Clientes Registrados: {total}", Fore.WHITE, Style.BRIGHT)

        # Schema Analysis
        self.print_sub_header("Schema e Tipos de Dados")
        self.log(str(self.df_clients.dtypes))

        # Null Analysis
        self.print_sub_header("Valores Nulos")
        null_counts = self.df_clients.isnull().sum()
        if null_counts.sum() > 0:
            self.log(str(null_counts[null_counts > 0]))
        else:
            self.log("Nenhum valor nulo encontrado nas colunas principais.", Fore.GREEN)

        # Duplicates
        self.print_sub_header("Verificação de Duplicatas")
        if 'Alias' in self.df_clients.columns:
            duplicates = self.df_clients[self.df_clients.duplicated('Alias', keep=False)]
            if not duplicates.empty:
                self.log("ALERTA: Alias duplicados encontrados!", Fore.RED)
                self.log(str(duplicates['Alias']))
            else:
                self.log("✔ Nenhum Alias duplicado.", Fore.GREEN)
        
        if 'CodCliente' in self.df_clients.columns:
            duplicates = self.df_clients[self.df_clients.duplicated('CodCliente', keep=False)]
            if not duplicates.empty:
                self.log("ALERTA: Códigos de Cliente duplicados encontrados!", Fore.RED)
                self.log(str(duplicates['CodCliente']))
            else:
                self.log("✔ Nenhum CodCliente duplicado.", Fore.GREEN)

    def analyze_services(self):
        self.print_header("ANÁLISE DE SERVIÇOS")
        
        try:
            self.df_services = self.repository.get_services_dataframe()
        except Exception as e:
            self.log(f"Erro ao ler aba 'baseServicos' via Repositório: {e}", Fore.RED)
            return

        # Basic Stats
        total = len(self.df_services)
        self.log(f"Total de Serviços Registrados: {total}", Fore.WHITE, Style.BRIGHT)

        # Schema Analysis
        self.print_sub_header("Schema e Tipos de Dados")
        self.log(str(self.df_services.dtypes))

        # Orphan Check
        self.print_sub_header("Integridade Relacional (Clientes Órfãos)")
        if self.df_clients is not None and 'AliasCliente' in self.df_services.columns:
            valid_clients = set(self.df_clients['Alias'].dropna())
            service_clients = set(self.df_services['AliasCliente'].dropna())
            
            orphans = service_clients - valid_clients
            if orphans:
                self.log("ALERTA: Serviços apontando para clientes inexistentes:", Fore.RED)
                for o in orphans:
                    self.log(f" - {o}")
            else:
                self.log("✔ Todos os serviços pertencem a clientes válidos.", Fore.GREEN)

    def analyze_folders(self):
        self.print_header("SINCRONIZAÇÃO DE PASTAS")
        
        if self.df_clients is None:
            self.log("Pulei análise de pastas pois não carreguei clientes.", Fore.RED)
            return

        db_aliases = set(self.df_clients['Alias'].dropna())
        
        try:
            # Use repository to list folders if possible, or direct access if repository method is limited
            # Repository has list_client_folders()
            folder_aliases = self.repository.list_client_folders()
        except Exception as e:
            self.log(f"Erro ao listar pastas via Repositório: {e}", Fore.RED)
            return

        # DB vs Folder
        missing_folders = db_aliases - folder_aliases
        extra_folders = folder_aliases - db_aliases - set(config.ignored_folders)

        self.print_sub_header("Clientes no DB sem Pasta (Faltando)")
        if missing_folders:
            self.log(f"Encontrados {len(missing_folders)} clientes sem pasta:", Fore.RED)
            for m in missing_folders:
                self.log(f" - {m}")
        else:
            self.log("✔ Todos os clientes do DB possuem pasta.", Fore.GREEN)

        self.print_sub_header("Pastas sem Cliente no DB (Não Registrados)")
        if extra_folders:
            self.log(f"Encontradas {len(extra_folders)} pastas não registradas no DB:", Fore.YELLOW)
            for e in extra_folders:
                self.log(f" - {e}")
        else:
            self.log("✔ Todas as pastas estão registradas no DB.", Fore.GREEN)

    def _get_latest_info_file(self, folder, alias, suffix):
        """Helper to find latest INFO file."""
        files = list(folder.glob(f"*_INFO-{alias}.md"))
        if not files:
            return None
        # Sort by name (assuming standard naming convention)
        files.sort(key=lambda f: f.name, reverse=True)
        return files[0]

    def _read_keys_from_md(self, path):
        """Reads keys from MD file."""
        keys = set()
        data = {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        keys.add(key)
                        data[key] = value.strip()
        except Exception as e:
            self.log(f"Erro ao ler {path.name}: {e}", Fore.RED)
        return keys, data

    def analyze_info_files(self):
        self.print_header("ANÁLISE DE ARQUIVOS INFO")
        
        if self.df_clients is None:
            return

        self.print_sub_header("Verificação de INFO-CLIENTE.md")
        
        # Iterate over clients in DB that have folders
        for _, row in self.df_clients.iterrows():
            alias = row['Alias']
            client_name = row.get('NomeCliente', 'N/A')
            
            folder = self.base_pasta_clientes / alias
            if not folder.exists():
                continue

            info_file = self._get_latest_info_file(folder, alias, "CLIENTE")
            
            if not info_file:
                self.log(f"✘ {alias}: Arquivo INFO-CLIENTE não encontrado.", Fore.RED)
                continue

            # Check Keys
            found_keys, data = self._read_keys_from_md(info_file)
            missing_keys = EXPECTED_CLIENT_KEYS - found_keys
            
            if missing_keys:
                self.log(f"⚠ {alias}: Faltando chaves no INFO-CLIENTE:", Fore.YELLOW)
                for k in missing_keys:
                    self.log(f"   - {k}")
            
            # Check Coherence (DB vs File)
            file_name = data.get('@nomeCliente', '')
            if file_name and file_name != client_name:
                 self.log(f"⚠ {alias}: Divergência de Nome (DB: '{client_name}' vs Arquivo: '{file_name}')", Fore.MAGENTA)

        self.print_sub_header("Verificação de INFO-SERVICO.md")
        
        # Iterate over services
        if self.df_services is not None:
             for _, row in self.df_services.iterrows():
                client_alias = row['AliasCliente']
                service_alias = row['Alias']
                
                if pd.isna(client_alias) or pd.isna(service_alias):
                    continue

                folder = self.base_pasta_clientes / client_alias / service_alias
                if not folder.exists():
                    continue

                info_file = self._get_latest_info_file(folder, service_alias, "SERVICO")
                
                if not info_file:
                    self.log(f"✘ {client_alias}/{service_alias}: Arquivo INFO-SERVICO não encontrado.", Fore.RED)
                    continue

                # Check Keys
                found_keys, data = self._read_keys_from_md(info_file)
                missing_keys = EXPECTED_SERVICE_KEYS - found_keys
                
                if missing_keys:
                    self.log(f"⚠ {client_alias}/{service_alias}: Faltando chaves no INFO-SERVICO:", Fore.YELLOW)
                    # Only show first 5 missing to avoid spam
                    for k in list(missing_keys)[:5]:
                        self.log(f"   - {k}")
                    if len(missing_keys) > 5:
                        self.log(f"   ... e mais {len(missing_keys)-5} chaves.")

    def run(self):
        if self.check_files():
            self.analyze_clients()
            self.analyze_services()
            self.analyze_folders()
            self.analyze_info_files()
        
        sep = '='*60
        self.log(f"\n{sep}", Fore.CYAN)
        self.log(f"{'FIM DA ANÁLISE'.center(60)}", Fore.CYAN)
        self.log(f"{sep}", Fore.CYAN)
        
        self.save_report()


__title__ = "Diagnóstico do Sistema (Debug DB)"

def main():
    debugger = DatabaseDebugger()
    debugger.run()

if __name__ == "__main__":
    main()
