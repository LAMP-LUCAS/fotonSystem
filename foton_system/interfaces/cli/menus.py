import sys
import os
from typing import Optional
from foton_system.modules.clients.application.use_cases.client_service import ClientService
from foton_system.modules.documents.application.use_cases.document_service import DocumentService
from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import ExcelClientRepository
from foton_system.modules.documents.infrastructure.adapters.python_docx_adapter import PythonDocxAdapter
from foton_system.modules.documents.infrastructure.adapters.python_pptx_adapter import PythonPPTXAdapter
from foton_system.modules.productivity.pomodoro import PomodoroTimer
from foton_system.modules.shared.infrastructure.config.logger import setup_logger
from foton_system.interfaces.cli.ui_provider import UIProvider, get_ui_provider
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

logger = setup_logger()

class MenuSystem:
    def __init__(self, ui_provider: Optional[UIProvider] = None):
        """
        Initialize MenuSystem with optional UI provider.
        
        Args:
            ui_provider: UIProvider instance for TUI/GUI interactions.
                        If None, auto-detects based on environment.
        """
        # UI Provider (TUI or GUI)
        self.ui = ui_provider or get_ui_provider('auto')
        
        # Dependency Injection Wiring
        self.client_repo = ExcelClientRepository()
        self.client_service = ClientService(self.client_repo)

        self.docx_adapter = PythonDocxAdapter()
        self.pptx_adapter = PythonPPTXAdapter()
        self.document_service = DocumentService(self.docx_adapter, self.pptx_adapter)

    def print_success(self, message):
        print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")

    def print_error(self, message):
        print(f"{Fore.RED}{message}{Style.RESET_ALL}")

    def print_warning(self, message):
        print(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")

    def print_header(self, message):
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{message}{Style.RESET_ALL}")

    def display_main_menu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════════════════╗")
        print(f"║{Style.BRIGHT}{' FOTON SYSTEM '.center(58)}{Style.NORMAL}{Fore.CYAN}║")
        print(f"╠══════════════════════════════════════════════════════════╣")
        options = [
            ("1", "Gerenciar Clientes"),
            ("2", "Gerenciar Serviços"),
            ("3", "Documentos (PPTX/DOCX)"),
            ("4", "Produtividade (Pomodoro)"),
            ("5", "Configurações do Sistema"),
            ("6", "Instalação / Atalhos"),
            ("7", "Modo Sentinela (Watcher)"),
            ("0", "Sair")
        ]
        for key, label in options:
            print(f"{Fore.CYAN}║ {Fore.YELLOW}{key}. {Fore.WHITE}{label.ljust(53)}{Fore.CYAN}║")
        print(f"╚══════════════════════════════════════════════════════════╝")
        return input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha uma opção: {Style.RESET_ALL}").strip()

    def display_clients_menu(self):
        self.print_header("--- Gerenciar Clientes ---")
        print("1. Sincronizar Base (Pastas -> DB)")
        print("2. Sincronizar Pastas (DB -> Pastas)")
        print("3. Criar Novo Cliente")
        print("4. Buscar Cliente")
        print("5. Sincronizar Cadastro (DB <-> Arquivo)")
        print("0. Voltar")
        return input(f"{Fore.YELLOW}Escolha uma opção: {Style.RESET_ALL}")

    def display_services_menu(self):
        self.print_header("--- Gerenciar Serviços ---")
        print("1. Sincronizar Base (Pastas -> DB)")
        print("2. Sincronizar Pastas (DB -> Pastas) [Todos]")
        print("3. Sincronizar Pastas (DB -> Pastas) [Por Cliente]")
        print("4. Sincronizar Cadastro (DB <-> Arquivo)")
        print("0. Voltar")
        return input(f"{Fore.YELLOW}Escolha uma opção: {Style.RESET_ALL}")

    def display_documents_menu(self):
        self.print_header("--- Documentos ---")
        print("1. Gerar Proposta (PPTX)")
        print("2. Gerar Contrato (DOCX)")
        print("0. Voltar")
        return input(f"{Fore.YELLOW}Escolha uma opção: {Style.RESET_ALL}")

    def display_productivity_menu(self):
        self.print_header("--- Produtividade ---")
        print("1. Iniciar Pomodoro")
        print("0. Voltar")
        return input(f"{Fore.YELLOW}Escolha uma opção: {Style.RESET_ALL}")

    def run(self):
        try:
            while True:
                choice = self.display_main_menu()

                if choice == '1':
                    self.handle_clients()
                elif choice == '2':
                    self.handle_services()
                elif choice == '3':
                    self.handle_documents()
                elif choice == '4':
                    self.handle_productivity()
                elif choice == '5':
                    self.handle_settings()
                elif choice == '6':
                    self.handle_installation()
                elif choice == '0':
                    print("Saindo...")
                    sys.exit()
                else:
                    self.print_error("Opção inválida.")
        except KeyboardInterrupt:
            print("\n")
            self.print_warning("Interrupção detectada. Encerrando o sistema com segurança...")
            sys.exit()

    def handle_installation(self):
        from foton_system.modules.shared.infrastructure.services.install_service import InstallService
        self.print_header("--- Instalação ---")
        print("Isso criará atalhos na Área de Trabalho e Menu Iniciar apontando para este executável.")
        print("Também garantirá que a pasta de configuração do usuário exista.")
        
        if input("\nDeseja prosseguir? (S/N): ").upper() == 'S':
            try:
                InstallService().install()
                self.print_success("Instalação realizada com sucesso!")
            except Exception as e:
                logger.error(f"Erro crítico no menu de instalação: {e}", exc_info=True)
                self.print_error(f"Erro na instalação: {e}")
            input("Pressione Enter para voltar...")

    def handle_clients(self):
        while True:
            choice = self.display_clients_menu()
            if choice == '1':
                self.client_service.sync_clients_db_from_folders()
            elif choice == '2':
                self.client_service.sync_client_folders_from_db()
            elif choice == '3':
                self.create_client_ui()
            elif choice == '4':
                self.search_client_ui()
            elif choice == '5':
                self.print_header("--- Sincronizar Cadastro (Clientes) ---")
                print("1. Exportar (DB -> Arquivo)")
                print("2. Importar (Arquivo -> DB)")
                sub = input("Escolha: ")
                if sub == '1':
                    self.client_service.export_client_data()
                elif sub == '2':
                    self.client_service.import_client_data()
            elif choice == '0':
                break
            else:
                self.print_error("Opção inválida.")

    def handle_services(self):
        while True:
            choice = self.display_services_menu()
            if choice == '1':
                self.client_service.sync_services_db_from_folders()
            elif choice == '2':
                self.client_service.sync_service_folders_from_db()
            elif choice == '3':
                alias = input("Digite o Alias do Cliente: ").strip()
                if alias:
                    self.client_service.sync_service_folders_from_db(client_alias=alias)
            elif choice == '4':
                self.print_header("--- Sincronizar Cadastro (Serviços) ---")
                print("1. Exportar (DB -> Arquivo)")
                print("2. Importar (Arquivo -> DB)")
                sub = input("Escolha: ")
                if sub == '1':
                    self.client_service.export_service_data()
                elif sub == '2':
                    self.client_service.import_service_data()
            elif choice == '0':
                break
            else:
                self.print_error("Opção inválida.")

    def handle_documents(self):
        while True:
            choice = self.display_documents_menu()
            if choice == '1':
                self.generate_document_ui('pptx')
            elif choice == '2':
                self.generate_document_ui('docx')
            elif choice == '0':
                break
            else:
                self.print_error("Opção inválida.")

    def handle_productivity(self):
        while True:
            choice = self.display_productivity_menu()
            if choice == '1':
                self.start_pomodoro_ui()
            elif choice == '0':
                break
            else:
                self.print_error("Opção inválida.")

    def handle_settings(self):
        from foton_system.modules.shared.infrastructure.config.config import Config
        config = Config()

        while True:
            choice = self.display_settings_menu(config)

            if choice == '1':
                self.update_setting_ui(config, 'caminho_pastaClientes', "Pasta de Clientes")
            elif choice == '2':
                self.update_setting_ui(config, 'caminho_templates', "Pasta de Templates")
            elif choice == '3':
                self.update_setting_ui(config, 'caminho_baseDados', "Arquivo de Base de Dados", is_file=True)
            elif choice == '4':
                self.handle_admin_tools()
            elif choice == '5':
                # Open Workspace Folder
                import os
                try:
                    os.startfile(config.workspace_path)
                    self.print_success(f"Abrindo pasta: {config.workspace_path}")
                except Exception as e:
                    self.print_error(f"Erro ao abrir pasta: {e}")
            elif choice == '0':
                break
            else:
                self.print_error("Opção inválida.")

    def display_settings_menu(self, config):
        self.print_header("--- Configurações ---")
        print(f"1. Pasta de Clientes: {config.get('caminho_pastaClientes')}")
        print(f"2. Pasta de Templates: {config.get('caminho_templates')}")
        print(f"3. Base de Dados: {config.get('caminho_baseDados')}")
        print("4. Ferramentas Administrativas")
        print(f"5. Abrir Pasta do Sistema (Workspace): {config.workspace_path}")
        print("0. Voltar")
        return input(f"{Fore.YELLOW}Para alterar, digite o número da opção: {Style.RESET_ALL}")

    def update_setting_ui(self, config, key, title, is_file=False):
        print(f"\nSelecione o novo local para: {title}")

        if is_file:
            path = self.ui.select_file(f"Selecione: {title}")
        else:
            path = self.ui.select_directory(f"Selecione: {title}")

        if path:
            # Normalize path separators
            path = os.path.normpath(str(path))

            config.set(key, path)
            config.save()
            self.print_success(f"Configuração atualizada com sucesso!\nNovo valor: {path}")
        else:
            self.print_warning("Operação cancelada.")


    def create_client_ui(self):
        self.print_header("--- Novo Cliente ---")
        nome = input("Nome do Cliente: ")
        alias = input("Alias (Apelido da Pasta): ")
        telefone = input("Telefone: ")

        data = {
            'NomeCliente': nome,
            'Alias': alias,
            'TelefoneCliente': telefone
        }

        try:
            self.client_service.create_client(data)
            self.print_success("Cliente criado com sucesso!")
        except ValueError as ve:
            self.print_error(f"Erro de Validação: {ve}")
        except Exception as e:
            self.print_error(f"Erro ao criar cliente: {e}")

    def search_client_ui(self):
        self.print_header("--- Buscar Cliente ---")
        term = input("Digite o nome ou alias para buscar: ").strip().lower()
        if not term:
            return

        try:
            df = self.client_repo.get_clients_dataframe()
            # Filter by Name or Alias (case insensitive)
            mask = (
                df['NomeCliente'].astype(str).str.lower().str.contains(term, na=False) |
                df['Alias'].astype(str).str.lower().str.contains(term, na=False)
            )
            results = df[mask]

            if results.empty:
                self.print_warning("Nenhum cliente encontrado.")
            else:
                self.print_success(f"\n{len(results)} clientes encontrados:")
                for _, row in results.iterrows():
                    print(f"- {row['NomeCliente']} (Alias: {row['Alias']})")

        except Exception as e:
            self.print_error(f"Erro ao buscar clientes: {e}")

    def generate_document_ui(self, doc_type):
        from foton_system.modules.shared.infrastructure.config.config import Config
        from pathlib import Path

        self.print_header(f"--- Gerar Documento ({doc_type.upper()}) ---")

        # 1. Select Client Folder via UI Provider (TUI or GUI)
        print("Selecione a pasta do cliente...")
        client_folder = self.ui.select_directory("Selecione a Pasta do Cliente")

        if not client_folder:
            self.print_warning("Nenhuma pasta selecionada.")
            return

        client_path = Path(client_folder)
        print(f"Pasta selecionada: {client_path}")


        # 2. Check/Create Data File Pipeline
        data_files = self.document_service.list_client_data_files(client_path)

        selected_file = None

        if data_files:
            print("\nArquivos de dados encontrados:")
            for i, f in enumerate(data_files):
                print(f"{i + 1}. {f.name}")
            print(f"{len(data_files) + 1}. Criar novo arquivo")

            try:
                choice = int(input("Escolha uma opção: "))
                if 1 <= choice <= len(data_files):
                    selected_file = data_files[choice - 1]
                elif choice == len(data_files) + 1:
                    selected_file = self._create_new_data_file_ui(client_path)
                else:
                    self.print_error("Opção inválida.")
                    return
            except ValueError:
                self.print_error("Entrada inválida.")
                return
        else:
            self.print_warning("\nNenhum arquivo de dados encontrado.")
            create = input("Deseja criar um novo arquivo? (S/N): ").upper()
            if create == 'S':
                selected_file = self._create_new_data_file_ui(client_path)
            else:
                return

        if not selected_file:
            return

        print(f"Arquivo selecionado: {selected_file.name}")

        # Option to edit data file?
        edit = input("Deseja abrir o arquivo de dados para edição antes de continuar? (S/N): ").upper()
        if edit == 'S':
            import os
            os.startfile(selected_file)
            input("Pressione Enter após salvar e fechar o arquivo de dados...")

        # 3. Select Template
        templates = self.document_service.list_templates(doc_type)
        if not templates:
            self.print_warning("Nenhum template encontrado.")
            return

        print("\nSelecione o Template:")
        template_name = self._select_from_list(templates)
        if not template_name:
            return

        template_path = Config().templates_path / template_name

        # 4. Output Path (same as client folder)
        default_output = f"Proposta_{client_path.name}"
        output_name = input(f"Nome do arquivo de saída (padrão: {default_output}): ") or default_output
        if doc_type == 'pptx' and not output_name.endswith('.pptx'):
            output_name += '.pptx'
        elif doc_type == 'docx' and not output_name.endswith('.docx'):
            output_name += '.docx'

        output_path = client_path / output_name

        # Validate Keys before generation
        missing = self.document_service.validate_template_keys(str(template_path), str(selected_file), doc_type)
        if missing:
            self.print_warning(f"\n[AVISO] As seguintes chaves estão no template mas não no arquivo de dados:")
            for k in missing:
                print(f" - {k}")

            from foton_system.modules.shared.infrastructure.config.config import Config
            if Config().clean_missing_variables:
                print(f"Elas serão substituídas por '{Config().missing_variable_placeholder}'.")

            confirm = input("Deseja continuar mesmo assim? (S/N): ").upper()
            if confirm != 'S':
                self.print_warning("Operação cancelada.")
                return

        try:
            self.document_service.generate_document(str(template_path), str(selected_file), str(output_path), doc_type)   
            self.print_success(f"Documento gerado com sucesso em: {output_path}")

            # Open folder via UI Provider
            self.ui.open_folder(client_path)

        except Exception as e:
            self.print_error(f"Erro ao gerar documento: {e}")


    def _select_from_list(self, items):
        for i, item in enumerate(items):
            print(f"{i + 1}. {item}")

        try:
            choice = int(input(f"{Fore.YELLOW}Digite o número da opção: {Style.RESET_ALL}"))
            if 1 <= choice <= len(items):
                return items[choice - 1]
            else:
                self.print_error("Opção inválida.")
                return None
        except ValueError:
            self.print_error("Entrada inválida.")
            return None

    def _create_new_data_file_ui(self, client_path):
        self.print_header("--- Criar Novo Arquivo de Dados ---")
        print("Padrão: 02-{COD}_DOC_PC_{VER}_{REV}_{DESC}.md")

        cod = input("Código do Serviço (COD) [ex: 001]: ")
        if not cod:
            self.print_error("Código é obrigatório.")
            return None

        ver = input("Versão (VER) [padrão: 00]: ") or "00"
        rev = input("Revisão (REV) [padrão: R00]: ") or "R00"
        desc = input("Descrição (DESC) [padrão: PROPOSTA]: ") or "PROPOSTA"

        return self.document_service.create_custom_data_file(client_path, cod, ver, rev, desc)

    def start_pomodoro_ui(self):
        from foton_system.modules.shared.infrastructure.config.config import Config
        config = Config()

        try:
            # Load defaults
            default_work = config.pomodoro_work_time
            default_short = config.pomodoro_short_break
            default_long = config.pomodoro_long_break
            default_cycles = config.pomodoro_cycles

            self.print_header("--- Iniciar Pomodoro ---")
            print(f"Configuração Atual: Trabalho={default_work}m, Curta={default_short}m, Longa={default_long}m, Ciclos={default_cycles}")

            # Linking
            client_alias = None
            service_alias = None
            link = input("Deseja vincular a um cliente? (S/N): ").upper()
            if link == 'S':
                # Reuse search or list? Let's use search for quick access or list if empty
                # For simplicity, let's ask for name/alias search
                term = input("Digite o nome ou alias do cliente: ").strip()
                if term:
                    df = self.client_repo.get_clients_dataframe()
                    mask = (
                        df['NomeCliente'].astype(str).str.lower().str.contains(term.lower(), na=False) |
                        df['Alias'].astype(str).str.lower().str.contains(term.lower(), na=False)
                    )
                    results = df[mask]
                    if not results.empty:
                        # Auto-select first or ask? Let's ask if multiple, or just take first for speed
                        if len(results) > 1:
                            print(f"{len(results)} clientes encontrados. Usando o primeiro: {results.iloc[0]['NomeCliente']}")
                        client_alias = results.iloc[0]['Alias']
                        self.print_success(f"Vinculado ao cliente: {client_alias}")

                        service_input = input("Nome do Serviço (opcional): ").strip()
                        if service_input:
                            service_alias = service_input
                    else:
                        self.print_warning("Cliente não encontrado. Seguindo sem vínculo.")

            # Custom overrides
            change = input("Deseja alterar os tempos? (S/N): ").upper()
            if change == 'S':
                work = float(input(f"Tempo de trabalho (min) [{default_work}]: ") or default_work)
                short = float(input(f"Pausa curta (min) [{default_short}]: ") or default_short)
                long = float(input(f"Pausa longa (min) [{default_long}]: ") or default_long)
                cycles = int(input(f"Ciclos [{default_cycles}]: ") or default_cycles)
            else:
                work, short, long, cycles = default_work, default_short, default_long, default_cycles

            timer = PomodoroTimer(work, short, long, cycles, client_alias, service_alias)
            timer.run()
        except ValueError:
            self.print_error("Valores inválidos.")
        except KeyboardInterrupt:
            print("\n")
            self.print_warning("Operação interrompida.")

    def handle_admin_tools(self):
        try:
            from foton_system.scripts.admin_launcher import main_menu
            main_menu()
        except ImportError:
            self.print_error("Erro: Launcher administrativo não encontrado.")
        except Exception as e:
            self.print_error(f"Erro ao abrir ferramentas administrativas: {e}")
