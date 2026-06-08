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
from foton_system.modules.shared.infrastructure.services.tip_service import TipService
from foton_system.modules.shared.infrastructure.services.environment_porter import get_porter, SystemProfile
from foton_system.interfaces.cli.ui_provider import UIProvider, get_ui_provider
from foton_system.interfaces.cli.views.tui_layout import TUILayout
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
        # Ambiente e Provedor de UI
        self.porter = get_porter()
        self.ui = ui_provider or get_ui_provider('auto')
        
        # Dependency Injection Wiring
        self.client_repo = ExcelClientRepository()
        self.client_service = ClientService(self.client_repo)

        self.docx_adapter = PythonDocxAdapter()
        self.pptx_adapter = PythonPPTXAdapter()
        self.document_service = DocumentService(self.docx_adapter, self.pptx_adapter)

        self.tip_service = TipService()

        # Ensure database exists to prevent pipeline errors
        self._ensure_database_exists()

    def print_success(self, message):
        print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")

    def print_error(self, message):
        print(f"{Fore.RED}{message}{Style.RESET_ALL}")

    def print_warning(self, message):
        print(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")

    def print_header(self, message):
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{message}{Style.RESET_ALL}")

    def _ensure_database_exists(self):
        """Checks if the database file exists, and creates it if missing."""
        from foton_system.modules.shared.infrastructure.config.config import Config
        import pandas as pd
        
        try:
            config = Config()
            db_path = config.get('caminho_baseDados')
            
            if not db_path:
                return

            # Ensure directory exists
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)

            if not os.path.exists(db_path):
                self.print_warning(f"Base de dados não encontrada em: {db_path}")
                self.print_warning("Inicializando nova base de dados com estrutura completa...")
                
                # Create Excel with proper structure (multiple sheets)
                with pd.ExcelWriter(db_path, engine='openpyxl') as writer:
                    # Sheet: baseClientes
                    df_clientes = pd.DataFrame(columns=[
                        'ID', 'NomeCliente', 'Alias', 'TelefoneCliente', 'Email',
                        'CPF_CNPJ', 'Endereco', 'CidadeProposta', 'EstadoCivil', 'Profissao'
                    ])
                    df_clientes.to_excel(writer, sheet_name='baseClientes', index=False)
                    
                    # Sheet: baseServicos
                    df_servicos = pd.DataFrame(columns=[
                        'ID', 'AliasCliente', 'Alias', 'CodServico', 'Modalidade', 'Ano',
                        'Demanda', 'AreaTotal', 'AreaCoberta', 'AreaDescoberta',
                        'Detalhes', 'Estilo', 'Ambientes', 'ValorProposta', 'ValorContrato'
                    ])
                    df_servicos.to_excel(writer, sheet_name='baseServicos', index=False)
                
                self.print_success("Base de dados criada com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao verificar/criar base de dados: {e}", exc_info=True)

    def display_main_menu(self):
        TUILayout.clear()
        TUILayout.print_header("FOTON SYSTEM")
        
        # Mapeamento Dinâmico de Opções
        all_options = [
            ("1", "Gerenciar Clientes", True),
            ("2", "Gerenciar Serviços", True),
            ("3", "Preencher Ficha (Interface)", self.porter.can_use_feature("webview")),
            ("4", "Documentos (PPTX/DOCX)", True),
            ("5", "Produtividade (Pomodoro)", True),
            ("6", "Configurações do Sistema", True),
            ("7", "Instalação / Atalhos", self.porter.can_use_feature("shortcuts")),
            ("8", "Modo Sentinela (Watcher)", self.porter.can_use_feature("watcher")),
            ("0", "Sair", True)
        ]
        
        # Filtra opções disponíveis
        active_options = [(k, l) for k, l, available in all_options if available]
        
        for key, label in active_options:
            TUILayout.print_menu_option(key, label)
        
        # Rodapé Didático
        try:
            tip = self.tip_service.get_random_tip("GERAL")
            TUILayout.print_tip(tip, "DICA")
        except Exception: pass

        TUILayout.print_footer()
        return input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha uma opção: {Style.RESET_ALL}").strip()

    def display_clients_menu(self):
        TUILayout.clear()
        TUILayout.print_header("GERENCIAR CLIENTES")
        
        options = [
            ("1", "Sincronizar Base (Pastas -> DB)"),
            ("2", "Sincronizar Pastas (DB -> Pastas)"),
            ("3", "Criar Novo Cliente"),
            ("4", "Buscar Cliente"),
            ("5", "Sincronizar Cadastro (DB <-> Arquivo)"),
            ("0", "Voltar")
        ]
        for key, label in options:
            TUILayout.print_menu_option(key, label)
        
        # Rodapé Didático Contextual
        try:
            tip = self.tip_service.get_random_tip("SSOT")
            TUILayout.print_tip(tip, "CLIENTE")
        except Exception: pass

        TUILayout.print_footer()
        return input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha uma opção: {Style.RESET_ALL}").strip()

    def display_services_menu(self):
        TUILayout.clear()
        TUILayout.print_header("GERENCIAR SERVIÇOS")
        
        options = [
            ("1", "Sincronizar Base (Pastas -> DB)"),
            ("2", "Sincronizar Pastas (DB -> Pastas) [Todos]"),
            ("3", "Sincronizar Pastas (DB -> Pastas) [Por Cliente]"),
            ("4", "Sincronizar Cadastro (DB <-> Arquivo)"),
            ("0", "Voltar")
        ]
        for key, label in options:
            TUILayout.print_menu_option(key, label)
        
        # Rodapé Didático Contextual
        try:
            tip = self.tip_service.get_random_tip("PRODUTIVIDADE")
            TUILayout.print_tip(tip, "SERVIÇO")
        except Exception: pass

        TUILayout.print_footer()
        return input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha uma opção: {Style.RESET_ALL}").strip()

    def display_documents_menu(self):
        TUILayout.clear()
        TUILayout.print_header("DOCUMENTOS")
        
        options = [
            ("1", "Gerar Proposta (PPTX)"),
            ("2", "Gerar Contrato (DOCX)"),
            ("3", "Validar Template (Pré-voo)"),
            ("0", "Voltar")
        ]
        for key, label in options:
            TUILayout.print_menu_option(key, label)
            
        # Rodapé Didático Contextual
        try:
            tip = self.tip_service.get_random_tip("FORMATACAO")
            TUILayout.print_tip(tip, "DOCS")
        except Exception: pass

        TUILayout.print_footer()
        return input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha uma opção: {Style.RESET_ALL}").strip()

    def display_productivity_menu(self):
        TUILayout.clear()
        TUILayout.print_header("PRODUTIVIDADE")
        
        options = [
            ("1", "Iniciar Pomodoro"),
            ("0", "Voltar")
        ]
        for key, label in options:
            TUILayout.print_menu_option(key, label)
            
        # Rodapé Didático Contextual
        try:
            tip = self.tip_service.get_random_tip("GERAL")
            TUILayout.print_tip(tip, "FOCO")
        except Exception: pass

        TUILayout.print_footer()
        return input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha uma opção: {Style.RESET_ALL}").strip()

    def display_settings_menu(self, config):
        TUILayout.clear()
        TUILayout.print_header("CONFIGURAÇÕES")
        
        # Exibe caminhos truncados para caber no menu se necessário
        TUILayout.print_menu_option("1", f"Pasta Clientes: {os.path.basename(config.get('caminho_pastaClientes'))}")
        TUILayout.print_menu_option("2", f"Pasta Templates: {os.path.basename(config.get('caminho_templates'))}")
        TUILayout.print_menu_option("3", f"Base de Dados: {os.path.basename(config.get('caminho_baseDados'))}")
        TUILayout.print_menu_option("4", "Ferramentas Administrativas")
        TUILayout.print_menu_option("5", "Abrir Pasta do Sistema (Workspace)")
        TUILayout.print_menu_option("0", "Voltar")
        
        # Rodapé Didático Contextual
        try:
            tip = self.tip_service.get_random_tip("SANDBOX")
            TUILayout.print_tip(tip, "CONFIG")
        except Exception: pass

        TUILayout.print_footer()
        return input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha uma opção: {Style.RESET_ALL}").strip()

    def run(self):
        try:
            while True:
                choice = self.display_main_menu()

                if choice == '1':
                    self.handle_clients()
                elif choice == '2':
                    self.handle_services()
                elif choice == '3':
                    self.handle_webview_interface()
                elif choice == '4':
                    self.handle_documents()
                elif choice == '5':
                    self.handle_productivity()
                elif choice == '6':
                    self.handle_settings()
                elif choice == '7':
                    self.handle_installation()
                elif choice == '8':
                    self.handle_watcher()
                elif choice == '0':
                    print("Saindo...")
                    sys.exit()
                else:
                    self.print_error("Opção inválida.")
        except KeyboardInterrupt:
            print("\n")
            self.print_warning("Interrupção detectada. Encerrando o sistema com segurança...")
            sys.exit()

    def handle_webview_interface(self):
        """Interface de preenchimento: Escolha entre Terminal ou Visual (Agnóstico)."""
        from pathlib import Path
        TUILayout.clear()
        TUILayout.print_header("PREENCHIMENTO DE FICHA")
        
        data_file = self.ui.select_file("Selecione o Arquivo de Dados (.md)", extensions=[".md"])
        if not data_file:
            self.print_warning("Nenhum arquivo selecionado.")
            return

        data_path = Path(data_file)
        
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Callback para salvar
            def save_fn(new_content):
                try:
                    with open(data_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    return True
                except Exception as e:
                    logger.error(f"Erro ao salvar: {e}")
                    return False

            # Obtém o filler adequado via Porteiro
            filler = self.porter.get_form_filler()
            
            # Se for servidor, ele já avisará que é TUI
            if self.porter.profile == SystemProfile.SERVER_HEADLESS:
                 filler.open_form(content, save_fn)
                 input("Pressione Enter para continuar...")
                 return

            # No Desktop, damos a opção de TUI ou Visual
            print(f"\n{Fore.YELLOW}Escolha o modo de preenchimento:{Style.RESET_ALL}")
            print("  [1] Terminal (Nativo)")
            print("  [2] Interface Rica (Visual/Web)")
            print("  [0] Cancelar")
            
            sub_choice = input(f"\n{Fore.YELLOW}>> Escolha: {Style.RESET_ALL}").strip()
            
            if sub_choice == '1':
                from foton_system.modules.documents.application.use_cases.tui_form_filler_use_case import TUIFormFillerUseCase
                tui_filler = TUIFormFillerUseCase(data_path)
                if tui_filler.execute():
                    self.print_success("\n✅ Ficha atualizada com sucesso via Terminal!")
                    input("Pressione Enter para continuar...")
            elif sub_choice == '2':
                print(f"🚀 Iniciando interface para: {data_path.name}")
                if not filler.open_form(content, save_fn):
                     self.print_error("Falha ao abrir interface visual.")
                     input("Enter...")
            else:
                self.print_warning("Operação cancelada.")
                
        except Exception as e:
            self.print_error(f"Erro no pipeline de interface: {e}")
            input("Pressione Enter para voltar...")

    def handle_installation(self):
        from foton_system.modules.shared.infrastructure.services.install_service import InstallService
        TUILayout.clear()
        TUILayout.print_header("INSTALAÇÃO E ATALHOS")
        
        print(f"\n  {Fore.WHITE}Isso criará atalhos na Área de Trabalho e Menu Iniciar.")
        print(f"  Garante também a pasta de configuração local.")
        
        # Dica Contextual
        try:
            tip = self.tip_service.get_random_tip("GERAL")
            TUILayout.print_tip(tip, "SETUP")
        except Exception: pass
        
        TUILayout.print_footer()
        
        if input(f"\n{Fore.YELLOW}Deseja prosseguir? (S/N): {Style.RESET_ALL}").upper() == 'S':
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
                input("Pressione Enter para continuar...")
            elif choice == '2':
                self.client_service.sync_client_folders_from_db()
                input("Pressione Enter para continuar...")
            elif choice == '3':
                self.create_client_ui()
                input("Pressione Enter para continuar...")
            elif choice == '4':
                self.search_client_ui()
                input("Pressione Enter para continuar...")
            elif choice == '5':
                self.handle_client_sync_menu()
            elif choice == '0':
                break
            else:
                self.print_error("Opção inválida.")

    def handle_client_sync_menu(self):
        while True:
            TUILayout.clear()
            TUILayout.print_header("SINCRONIZAR CADASTRO (CLIENTES)")
            TUILayout.print_menu_option("1", "Exportar (DB -> Arquivo INFO)")
            TUILayout.print_menu_option("2", "Importar (Arquivo INFO -> DB)")
            TUILayout.print_menu_option("0", "Voltar")
            TUILayout.print_footer()

            sub = input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha: {Style.RESET_ALL}")
            if sub == '1':
                self.client_service.export_client_data()
                input("Pressione Enter para continuar...")
            elif sub == '2':
                self.client_service.import_client_data()
                input("Pressione Enter para continuar...")
            elif sub == '0':
                break
            else:
                self.print_error("Opção inválida.")

    def handle_services(self):
        while True:
            choice = self.display_services_menu()
            if choice == '1':
                self.client_service.sync_services_db_from_folders()
                input("Pressione Enter para continuar...")
            elif choice == '2':
                self.client_service.sync_service_folders_from_db()
                input("Pressione Enter para continuar...")
            elif choice == '3':
                alias = input("Digite o Alias do Cliente: ").strip()
                if alias:
                    self.client_service.sync_service_folders_from_db(client_alias=alias)
                input("Pressione Enter para continuar...")
            elif choice == '4':
                self.handle_service_sync_menu()
            elif choice == '0':
                break
            else:
                self.print_error("Opção inválida.")

    def handle_service_sync_menu(self):
        while True:
            TUILayout.clear()
            TUILayout.print_header("SINCRONIZAR CADASTRO (SERVIÇOS)")
            TUILayout.print_menu_option("1", "Exportar (DB -> Arquivo INFO)")
            TUILayout.print_menu_option("2", "Importar (Arquivo INFO -> DB)")
            TUILayout.print_menu_option("0", "Voltar")
            TUILayout.print_footer()

            sub = input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha: {Style.RESET_ALL}")
            if sub == '1':
                self.client_service.export_service_data()
                input("Pressione Enter para continuar...")
            elif sub == '2':
                self.client_service.import_service_data()
                input("Pressione Enter para continuar...")
            elif sub == '0':
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
            elif choice == '3':
                self.validate_template_ui()
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
                self._open_workspace_folder(config)
            elif choice == '0':
                break
            else:
                self.print_error("Opção inválida.")

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
            input("Pressione Enter para continuar...")
        else:
            self.print_warning("Operação cancelada.")
            input("Pressione Enter para continuar...")


    def _open_workspace_folder(self, config):
        import sys
        import os
        import subprocess

        path = str(config.workspace_path)
        try:
            if sys.platform == 'win32':
                os.startfile(path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', path], check=True)
            else:
                subprocess.run(['xdg-open', path], check=True)
            self.print_success(f"Abrindo pasta: {path}")
        except Exception as e:
            self.print_error(f"Erro ao abrir pasta: {e}")
        input("Pressione Enter para continuar...")

    def create_client_ui(self):
        TUILayout.clear()
        TUILayout.print_header("NOVO CLIENTE")
        print("\n  Preencha os dados básicos:\n")
        nome = input("  Nome do Cliente: ")
        alias = input("  Alias (Apelido): ")
        telefone = input("  Telefone      : ")

        data = {
            'NomeCliente': nome,
            'Alias': alias,
            'TelefoneCliente': telefone
        }

        try:
            self.client_service.create_client(data)
            self.print_success("\n✅ Cliente criado com sucesso!")
        except ValueError as ve:
            self.print_error(f"\n❌ Erro de Validação: {ve}")
        except Exception as e:
            self.print_error(f"\n❌ Erro ao criar cliente: {e}")

    def search_client_ui(self):
        TUILayout.clear()
        TUILayout.print_header("BUSCAR CLIENTE")
        term = input("\n  Digite o nome ou alias: ").strip().lower()
        if not term:
            return

        try:
            df = self.client_repo.get_clients_dataframe()
            mask = (
                df['NomeCliente'].astype(str).str.lower().str.contains(term, na=False) |
                df['Alias'].astype(str).str.lower().str.contains(term, na=False)
            )
            results = df[mask]

            if results.empty:
                self.print_warning("\n📭 Nenhum cliente encontrado.")
            else:
                self.print_success(f"\n🔍 {len(results)} clientes encontrados:")
                for _, row in results.iterrows():
                    print(f"  - {row['NomeCliente']} (Alias: {row['Alias']})")

        except Exception as e:
            self.print_error(f"\n❌ Erro ao buscar clientes: {e}")

    def generate_document_ui(self, doc_type):
        from foton_system.modules.shared.infrastructure.config.config import Config
        from pathlib import Path

        TUILayout.clear()
        TUILayout.print_header(f"GERAR DOCUMENTO ({doc_type.upper()})")

        # 1. Select Client Folder
        print("\n  Selecione a pasta do cliente...")
        client_folder = self.ui.select_directory("Selecione a Pasta do Cliente")

        if not client_folder:
            self.print_warning("  Operação cancelada.")
            return

        client_path = Path(client_folder)
        
        # 2. Check/Create Data File Pipeline
        data_files = self.document_service.list_client_data_files(client_path)
        selected_file = None

        if data_files:
            print("\n  Arquivos de dados encontrados:")
            for i, f in enumerate(data_files):
                print(f"  {i + 1}. {f.name}")
            print(f"  {len(data_files) + 1}. Criar novo arquivo")

            try:
                choice = int(input("\n  Escolha uma opção: "))
                if 1 <= choice <= len(data_files):
                    selected_file = data_files[choice - 1]
                elif choice == len(data_files) + 1:
                    selected_file = self._create_new_data_file_ui(client_path)
                else:
                    self.print_error("  Opção inválida.")
                    return
            except ValueError:
                self.print_error("  Entrada inválida.")
                return
        else:
            self.print_warning("\n  Nenhum arquivo de dados encontrado.")
            create = input("  Deseja criar um novo arquivo? (S/N): ").upper()
            if create == 'S':
                selected_file = self._create_new_data_file_ui(client_path)
            else:
                return

        if not selected_file:
            return

        # 3. Select Template
        templates = self.document_service.list_templates(doc_type)
        if not templates:
            self.print_warning("  Nenhum template encontrado.")
            return

        print("\n  Selecione o Template:")
        template_name = self._select_from_list(templates)
        if not template_name:
            return

        template_path = Config().templates_path / template_name

        # 4. Output Path
        default_output = f"Proposta_{client_path.name}"
        output_name = input(f"\n  Nome de saída (padrão: {default_output}): ") or default_output
        if doc_type == 'pptx' and not output_name.endswith('.pptx'):
            output_name += '.pptx'
        elif doc_type == 'docx' and not output_name.endswith('.docx'):
            output_name += '.docx'

        output_path = client_path / output_name

        try:
            self.document_service.generate_document(str(template_path), str(selected_file), str(output_path), doc_type)   
            self.print_success(f"\n✅ Sucesso! Gerado em: {output_path}")
            self.ui.open_folder(client_path)
            input("\nPressione Enter para continuar...")
        except Exception as e:
            self.print_error(f"\n❌ Erro ao gerar: {e}")
            input("\nPressione Enter para continuar...")

    def _select_from_list(self, items):
        for i, item in enumerate(items):
            print(f"  {i + 1}. {item}")

        try:
            choice = int(input(f"\n  {Fore.YELLOW}Opção: {Style.RESET_ALL}"))
            if 1 <= choice <= len(items):
                return items[choice - 1]
            else:
                self.print_error("  Opção inválida.")
                return None
        except ValueError:
            self.print_error("  Entrada inválida.")
            return None

    def _create_new_data_file_ui(self, client_path):
        print("\n  Padrão: 02-{COD}_DOC_PC_{VER}_{REV}_{DESC}.md")
        cod = input("  Código (COD) [ex: 001]: ")
        if not cod:
            self.print_error("  Código é obrigatório.")
            return None

        ver = input("  Versão (VER) [00]: ") or "00"
        rev = input("  Revisão (REV) [R00]: ") or "R00"
        desc = input("  Descrição (DESC) [PROPOSTA]: ") or "PROPOSTA"

        return self.document_service.create_custom_data_file(client_path, cod, ver, rev, desc)

    def start_pomodoro_ui(self):
        from foton_system.modules.shared.infrastructure.config.config import Config
        config = Config()
        TUILayout.clear()
        TUILayout.print_header("TIMER POMODORO")

        try:
            # Load defaults
            work = config.pomodoro_work_time
            short = config.pomodoro_short_break
            long = config.pomodoro_long_break
            cycles = config.pomodoro_cycles

            print(f"\n  Foco: {work}m | Pausa: {short}m | Ciclos: {cycles}")
            
            client_alias = None
            link = input("\n  Vincular a um cliente? (S/N): ").upper()
            if link == 'S':
                term = input("  Nome/Alias: ").strip()
                if term:
                    df = self.client_repo.get_clients_dataframe()
                    mask = df['Alias'].str.lower().str.contains(term.lower(), na=False)
                    res = df[mask]
                    if not res.empty:
                        client_alias = res.iloc[0]['Alias']
                        self.print_success(f"  Vínculo: {client_alias}")

            timer = PomodoroTimer(work, short, long, cycles, client_alias)
            timer.run()
        except Exception as e:
            self.print_error(f"Erro no timer: {e}")

    def handle_admin_tools(self):
        try:
            from foton_system.scripts.admin_launcher import main_menu
            main_menu()
        except Exception as e:
            self.print_error(f"Erro: {e}")

    def validate_template_ui(self):
        from foton_system.modules.shared.infrastructure.config.config import Config
        from pathlib import Path
        TUILayout.clear()
        TUILayout.print_header("VALIDAR TEMPLATE")

        print("\n  Selecione a pasta do cliente...")
        client_folder = self.ui.select_directory("Selecione a Pasta")
        if not client_folder: return

        client_path = Path(client_folder)
        data_files = self.document_service.list_client_data_files(client_path)
        if not data_files:
            self.print_warning("  Nenhum arquivo INFO encontrado.")
            return

        print("\n  Arquivos disponíveis:")
        for i, f in enumerate(data_files):
            print(f"  {i+1}. {f.name}")
        
        try:
            idx = int(input("\n  Escolha: ")) - 1
            selected_file = data_files[idx]
        except (ValueError, IndexError): return

        print("\n  Tipo: [1] PPTX | [2] DOCX")
        doc_type = 'pptx' if input("  Escolha: ") == '1' else 'docx'

        templates = self.document_service.list_templates(doc_type)
        print("\n  Templates:")
        template_name = self._select_from_list(templates)
        if not template_name: return

        template_path = Config().templates_path / template_name
        missing = self.document_service.validate_template_keys(str(template_path), str(selected_file), doc_type)

        if not missing:
            self.print_success("\n✅ TUDO PRONTO! Variáveis validadas.")
        else:
            self.print_warning(f"\n⚠️ FALTANDO {len(missing)} VARIÁVEIS:")
            for k in missing: print(f"  ❌ {k}")

        input("\nPressione Enter para voltar...")

    def handle_watcher(self):
        while True:
            TUILayout.clear()
            TUILayout.print_header("MODO SENTINELA (WATCHER)")
            
            options = [
                ("1", "Ativar Watcher"),
                ("2", "Desativar Watcher"),
                ("3", "Indexar Base de Conhecimento (RAG)"),
                ("4", "Consultar Conhecimento"),
                ("0", "Voltar")
            ]
            for key, label in options:
                TUILayout.print_menu_option(key, label)

            try:
                tip = self.tip_service.get_random_tip("IA")
                TUILayout.print_tip(tip, "SENTINELA")
            except Exception: pass

            TUILayout.print_footer()
            choice = input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha: {Style.RESET_ALL}").strip()

            if choice == '1':
                self.print_warning("  Iniciando Watcher...")
                try:
                    from foton_system.core.watcher.service import WatcherService
                    self._watcher = WatcherService()
                    self._watcher.start()
                    self.print_success("  Watcher ativado!")
                    input("Enter...")
                except Exception as e:
                    self.print_error(f"Erro: {e}")
                    input("Enter...")
            elif choice == '2':
                if hasattr(self, '_watcher') and self._watcher:
                    self._watcher.stop()
                    self.print_success("  Watcher desativado.")
                else:
                    self.print_warning("  Nenhum watcher ativo.")
                input("Enter...")
            elif choice == '3':
                self._index_knowledge_ui()
            elif choice == '4':
                self._query_knowledge_ui()
            elif choice == '0':
                break

    def _index_knowledge_ui(self):
        TUILayout.clear()
        TUILayout.print_header("INDEXAR CONHECIMENTO")
        print("\n  Escaneando documentos para RAG...")
        if input("\n  Prosseguir? (S/N): ").upper() != 'S': return

        try:
            from foton_system.core.ops.op_index_knowledge import OpIndexKnowledge
            op = OpIndexKnowledge(actor="User")
            res = op.execute()
            self.print_success(f"\n✅ Indexado: {res.get('files_scanned')} arquivos.")
        except Exception as e:
            self.print_error(f"Erro: {e}")
        input("\nEnter...")

    def _query_knowledge_ui(self):
        TUILayout.clear()
        TUILayout.print_header("CONSULTAR CONHECIMENTO")
        query = input("\n  Pergunta: ").strip()
        if not query: return

        try:
            from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
            op = OpQueryKnowledge(actor="User")
            res = op.execute(query=query)
            if res['status'] == 'EMPTY':
                self.print_warning("  Nada encontrado.")
            else:
                for i, r in enumerate(res['results'], 1):
                    print(f"\n  [{i}] {r['source']} ({r['score']:.0%})")
                    print(f"  {r['document'][:200]}...")
        except Exception as e:
            self.print_error(f"Erro: {e}")
        input("\nEnter...")
