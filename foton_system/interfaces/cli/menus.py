import sys
import os
from pathlib import Path
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

    def print_info(self, message):
        print(f"{Fore.CYAN}{message}{Style.RESET_ALL}")

    def print_breadcrumb(self, path: list):
        breadcrumb = " > ".join(path)
        print(f"\n  {Fore.CYAN}{breadcrumb}{Style.RESET_ALL}\n")

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
            ("---", "Operações", True),
            ("3", "Preencher Ficha (Interface)", self.porter.can_use_feature("webview")),
            ("4", "Documentos (PPTX/DOCX)", True),
            ("5", "Financeiro", True),
            ("---", "Ferramentas", True),
            ("6", "Produtividade (Pomodoro)", True),
            ("7", "Configurações do Sistema", True),
            ("8", "Instalação / Atalhos", self.porter.can_use_feature("install")),
            ("9", "Modo Sentinela (Watcher)", self.porter.can_use_feature("watcher")),
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
            ("---", "Pipeline"),
            ("3", "Pipeline Sincronização (Unificado)"),
            ("---", "Busca"),
            ("4", "Buscar Cliente"),
            ("---", "Cadastro"),
            ("5", "Cadastrar Cliente (com verificação)"),
            ("6", "Ler Ficha (INFO) do Cliente"),
            ("7", "Atualizar Ficha do Cliente"),
            ("---", "Manutenção"),
            ("8", "Preencher Códigos Faltantes"),
            ("9", "Remover Cliente (Soft Delete)"),
            ("10", "Restaurar Cliente"),
            ("---", "Serviços"),
            ("11", "Serviços do Cliente"),
            ("12", "Sincronizar Cadastro (DB <-> Arquivo)"),
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
        TUILayout.print_menu_option("---", "Ferramentas")
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
                
                # Keyboard shortcuts
                if choice.lower() == 'q':
                    print("Saindo...")
                    sys.exit()
                elif choice.lower() == 'h':
                    self.print_info("  Ajuda: Digite o número da opção ou 'q' para sair, 'h' para ajuda")
                    input("  Pressione Enter para continuar...")
                    continue
                elif choice.lower() == 'g':
                    self.global_search_ui()
                    continue
                elif choice == '00':
                    continue  # Already at main menu
                
                if choice == '1':
                    self.handle_clients()
                elif choice == '2':
                    self.handle_services()
                elif choice == '3':
                    self.handle_webview_interface()
                elif choice == '4':
                    self.handle_documents()
                elif choice == '5':
                    self.handle_finance()
                elif choice == '6':
                    self.handle_productivity()
                elif choice == '7':
                    self.handle_settings()
                elif choice == '8':
                    self.handle_installation()
                elif choice == '9':
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
                result = InstallService().install()
                if result == "KILL_SWITCH":
                    print(f"\n  {Fore.CYAN}⚡ O programa será fechado para concluir a instalação.{Style.RESET_ALL}")
                    print(f"  {Fore.CYAN}  Ele será reaberto automaticamente em instantes.{Style.RESET_ALL}")
                    print()
                    input("Pressione Enter para sair...")
                    os._exit(0)
                else:
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
                self.pipeline_sync_ui()
                input("Pressione Enter para continuar...")
            elif choice == '4':
                self.search_client_ui()
                input("Pressione Enter para continuar...")
            elif choice == '5':
                self.create_client_ui()
                input("Pressione Enter para continuar...")
            elif choice == '6':
                self.read_client_info_ui()
                input("Pressione Enter para continuar...")
            elif choice == '7':
                self.update_client_info_ui()
                input("Pressione Enter para continuar...")
            elif choice == '8':
                self.fill_missing_codes_ui()
                input("Pressione Enter para continuar...")
            elif choice == '9':
                self.remove_client_ui()
                input("Pressione Enter para continuar...")
            elif choice == '10':
                self.restore_client_ui()
                input("Pressione Enter para continuar...")
            elif choice == '11':
                self.handle_client_servicos_menu()
                input("Pressione Enter para continuar...")
            elif choice == '12':
                self.handle_client_sync_menu()
            elif choice == '0':
                break
            else:
                self.print_error("Opção inválida.")

    def read_client_info_ui(self):
        TUILayout.clear()
        TUILayout.print_header("LER FICHA DO CLIENTE")
        client_name = input("\n  Nome ou Alias do Cliente: ").strip()
        if not client_name:
            self.print_warning("Operação cancelada.")
            return
        try:
            result = self.client_service.read_client_info(client_name)
            print(f"\n  {Fore.CYAN}Arquivo: {result['filename']}{Style.RESET_ALL}")
            print(f"  {Fore.WHITE}{'─' * 60}{Style.RESET_ALL}")
            print(result['content'])
        except ValueError as e:
            self.print_error(f"\n❌ {e}")
        except Exception as e:
            self.print_error(f"\n❌ Erro: {e}")

    def update_client_info_ui(self):
        TUILayout.clear()
        TUILayout.print_header("ATUALIZAR FICHA DO CLIENTE")
        client_name = input("\n  Nome ou Alias do Cliente: ").strip()
        if not client_name:
            self.print_warning("Operação cancelada.")
            return
        secao = input("  Seção (ex: DADOS DO CLIENTE - PROPOSTA): ").strip()
        if not secao:
            self.print_warning("Seção não informada.")
            return
        print("  Digite o conteúdo (linha em branco para finalizar):")
        linhas = []
        while True:
            linha = input("  > ")
            if not linha:
                break
            linhas.append(linha)
        conteudo = "\n".join(linhas)
        if not conteudo:
            self.print_warning("Conteúdo vazio.")
            return
        try:
            backup = self.client_service.update_client_info(client_name, secao, conteudo)
            self.print_success(f"\n✅ Ficha atualizada! Backup: {backup}")
        except ValueError as e:
            self.print_error(f"\n❌ {e}")
        except Exception as e:
            self.print_error(f"\n❌ Erro: {e}")

    def fill_missing_codes_ui(self):
        TUILayout.clear()
        TUILayout.print_header("PREENCHER CÓDIGOS FALTANTES")
        print(f"\n  {Fore.YELLOW}Isso vai varrer o banco de dados e gerar códigos{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}para todos os registros que ainda não possuem{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}CodCliente ou CodServico.{Style.RESET_ALL}\n")
        if input("  Prosseguir? (S/N): ").upper() != 'S':
            self.print_warning("Operação cancelada.")
            return
        try:
            result = self.client_service.fill_missing_codes()
            clientes = result['clientes_alterados']
            servicos = result['servicos_alterados']
            if clientes:
                self.print_success(f"\n✅ {clientes} cliente(s) receberam código!")
            if servicos:
                self.print_success(f"✅ {servicos} serviço(s) receberam código!")
            if not clientes and not servicos:
                self.print_success("\n✅ Nenhum código faltante encontrado. Todos os registros já possuem código.")
        except Exception as e:
            self.print_error(f"\n❌ Erro: {e}")

    def remove_client_ui(self):
        TUILayout.clear()
        TUILayout.print_header("REMOVER CLIENTE")
        print(f"\n  {Fore.YELLOW}⚠️  ATENÇÃO: Esta operação marca o cliente como DELETADO.{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}    O cliente continuará visível na lista mas não aparecerá em buscas.{Style.RESET_ALL}\n")
        client_name = input("  Nome ou Alias do Cliente: ").strip()
        if not client_name:
            self.print_warning("Operação cancelada.")
            return
        if input(f"  Confirmar remoção de '{client_name}'? (S/N): ").upper() != 'S':
            self.print_warning("Operação cancelada.")
            return
        try:
            result = self.client_service.soft_delete_client(client_name)
            if result["success"]:
                self.print_success(f"\n✅ {result['message']}")
            else:
                self.print_error(f"\n❌ {result['error']}")
        except Exception as e:
            self.print_error(f"\n❌ Erro: {e}")

    def restore_client_ui(self):
        TUILayout.clear()
        TUILayout.print_header("RESTAURAR CLIENTE")
        try:
            deleted = self.client_service.get_deleted_clients()
            if not deleted:
                self.print_warning("\n  Nenhum cliente deletado encontrado.")
                return
            print(f"\n  Clientes deletados: {len(deleted)}\n")
            for c in deleted:
                print(f"  - {c.get('Alias', '?')} ({c.get('NomeCliente', '?')})")
            client_name = input("\n  Alias do cliente a restaurar: ").strip()
            if not client_name:
                self.print_warning("Operação cancelada.")
                return
            result = self.client_service.restore_client(client_name)
            if result["success"]:
                self.print_success(f"\n✅ {result['message']}")
            else:
                self.print_error(f"\n❌ {result['error']}")
        except Exception as e:
            self.print_error(f"\n❌ Erro: {e}")

    def pipeline_sync_ui(self):
        TUILayout.clear()
        TUILayout.print_header("PIPELINE SINCRONIZAÇÃO")
        print("\n  Direções disponíveis:")
        print("  1. pastas_to_db (descobrir novas pastas)")
        print("  2. db_to_pastas (criar pastas faltantes)")
        print("  3. bidir (ambas - padrão)")
        direcao_map = {'1': 'pastas_to_db', '2': 'db_to_pastas', '3': 'bidir'}
        choice = input("\n  Escolha [3]: ").strip() or '3'
        direcao = direcao_map.get(choice, 'bidir')
        try:
            from foton_system.modules.clients.application.use_cases.pipeline_sync import pipeline_sincronizacao, format_sync_report
            report = pipeline_sincronizacao(direcao)
            print(f"\n{format_sync_report(report)}")
        except Exception as e:
            self.print_error(f"\n❌ Erro: {e}")

    def global_search_ui(self):
        TUILayout.clear()
        TUILayout.print_header("BUSCA GLOBAL")
        query = input("\n  Digite o termo de busca: ").strip()
        if not query:
            self.print_warning("Termo vazio.")
            return
        try:
            df_clients = self.client_service.repository.get_clients_dataframe()
            df_services = self.client_service.repository.get_services_dataframe()
            
            results = []
            for _, row in df_clients.iterrows():
                if query.lower() in str(row.get('NomeCliente', '')).lower() or \
                   query.lower() in str(row.get('Alias', '')).lower():
                    results.append(f"  👤 Cliente: {row.get('Alias')} ({row.get('NomeCliente')})")
            
            for _, row in df_services.iterrows():
                if query.lower() in str(row.get('Alias', '')).lower():
                    results.append(f"  📁 Serviço: {row.get('AliasCliente')}/{row.get('Alias')}")
            
            if results:
                print(f"\n  Resultados para '{query}':\n")
                for r in results:
                    print(r)
            else:
                print(f"\n  Nenhum resultado para '{query}'.")
        except Exception as e:
            self.print_error(f"\n❌ Erro: {e}")

    def handle_client_servicos_menu(self):
        while True:
            TUILayout.clear()
            TUILayout.print_header("SERVIÇOS DO CLIENTE")
            self.print_breadcrumb(["Clientes", "Serviços"])
            TUILayout.print_menu_option("1", "Listar Serviços")
            TUILayout.print_menu_option("2", "Criar Estrutura de Serviço")
            TUILayout.print_menu_option("3", "Validar Códigos de Serviço")
            TUILayout.print_menu_option("4", "Corrigir Códigos de Serviço")
            TUILayout.print_menu_option("0", "Voltar")
            TUILayout.print_footer()
            sub = input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha: {Style.RESET_ALL}")
            if sub == '1':
                self.list_client_servicos_ui()
                input("Pressione Enter para continuar...")
            elif sub == '2':
                self.create_client_servico_ui()
                input("Pressione Enter para continuar...")
            elif sub == '3':
                self.validar_codigos_servicos_ui()
                input("Pressione Enter para continuar...")
            elif sub == '4':
                self.corrigir_codigos_servicos_ui()
                input("Pressione Enter para continuar...")
            elif sub == '0':
                break
            else:
                self.print_error("Opção inválida.")

    def list_client_servicos_ui(self):
        TUILayout.clear()
        TUILayout.print_header("LISTAR SERVIÇOS DO CLIENTE")
        client_name = input("\n  Nome ou Alias do Cliente: ").strip()
        if not client_name:
            self.print_warning("Operação cancelada.")
            return
        try:
            servicos = self.client_service.list_service_nodes(client_name)
            if not servicos:
                self.print_warning(f"\n  Nenhum serviço encontrado para '{client_name}'.")
                return
            self.print_success(f"\n  Serviços encontrados: {len(servicos)}")
            for svc in servicos:
                name = svc['name']
                parent = svc['parent']
                depth = svc['depth']
                indent = "  " * depth
                subdirs = ', '.join(s.name for s in Path(svc['path']).iterdir() if s.is_dir())
                print(f"  {indent}📁 {name} ({svc['file_count']} arquivo(s))")
                if subdirs:
                    print(f"  {indent}   Subpastas: {subdirs}")
        except ValueError as e:
            self.print_error(f"\n❌ {e}")
        except Exception as e:
            self.print_error(f"\n❌ Erro: {e}")

    def create_client_servico_ui(self):
        TUILayout.clear()
        TUILayout.print_header("CRIAR ESTRUTURA DE SERVIÇO")
        client_name = input("  Nome ou Alias do Cliente: ").strip()
        if not client_name:
            self.print_warning("Operação cancelada.")
            return
        service_name = input("  Nome do Serviço: ").strip()
        if not service_name:
            self.print_warning("Nome do serviço não informado.")
            return
        try:
            from foton_system.modules.shared.infrastructure.config.config import Config
            config = Config()
            client_path = self.client_service.resolve_client_path(client_name)
            client_alias = client_path.name
            service_path = client_path / service_name
            if service_path.exists():
                self.print_warning(f"\n  ⚠️ Já existe uma pasta: {service_path}")
                return
            from foton_system.modules.shared.infrastructure.validators import validate_filename
            if not validate_filename(service_name):
                self.print_error("Nome do serviço contém caracteres inválidos.")
                return
            entry = self.client_service.create_service_entry(client_alias, service_name)
            cod_servico = entry['CodServico']
            service_path.mkdir(parents=True, exist_ok=True)
            for sub in ['DOC', 'ADM', 'OP']:
                (service_path / sub).mkdir(exist_ok=True)
            from foton_system.modules.clients.application.use_cases.client_crud import _resolve_info_filename
            from foton_system.modules.clients.application.use_cases.client_crud import SERVICE_TEMPLATE_STR
            from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
            _, service_template = PathManager.get_info_pattern("servico") if False else (None, SERVICE_TEMPLATE_STR)
            filename = _resolve_info_filename("servico", codServico=cod_servico, aliasServico=service_name, versao="00", revisao="R00")
            info_path = service_path / filename
            info_path.write_text(service_template, encoding="utf-8")
            self.print_success(f"\n✅ Serviço '{service_name}' criado em {service_path}!")
            self.print_success(f"   🆔 Código do serviço: {cod_servico}")
        except ValueError as e:
            self.print_error(f"\n❌ {e}")
        except Exception as e:
            self.print_error(f"\n❌ Erro: {e}")

    def validar_codigos_servicos_ui(self):
        TUILayout.clear()
        TUILayout.print_header("VALIDAR CÓDIGOS DE SERVIÇO")
        try:
            result = self.client_service.fill_missing_codes()
            if result.get('servicos_alterados'):
                self.print_success(f"\n✅ {result['servicos_alterados']} serviço(s) receberam código automaticamente.")
            issues = self.client_service.validate_service_codes()
            if not issues:
                self.print_success("\n✅ Todos os códigos de serviço são válidos.")
                return
            n_issues = len(issues)
            self.print_warning(f"\n  ⚠️ {n_issues} código(s) de serviço com problema:")
            for iss in issues:
                svc_label = f"{iss['client_alias']}/{iss['service_alias']}"
                print(f"\n    [{iss['issue'].upper()}] {svc_label}")
                print(f"      Código: '{iss['cod_servico']}'")
                print(f"      Sugestão: {iss['suggested_fix']}")
        except Exception as e:
            self.print_error(f"\n❌ Erro: {e}")

    def corrigir_codigos_servicos_ui(self):
        TUILayout.clear()
        TUILayout.print_header("CORRIGIR CÓDIGOS DE SERVIÇO")
        try:
            result = self.client_service.fill_missing_codes()
            if result.get('servicos_alterados'):
                self.print_success(f"\n✅ {result['servicos_alterados']} serviço(s) receberam código automaticamente.")
            issues = self.client_service.validate_service_codes()
            if not issues:
                self.print_success("\n✅ Todos os códigos de serviço já são válidos.")
                return
            fixed = self.client_service.fix_service_codes(issues)
            self.print_success(f"\n✅ {fixed} código(s) de serviço corrigido(s) automaticamente.")
        except Exception as e:
            self.print_error(f"\n❌ Erro: {e}")

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

    def display_finance_menu(self):
        TUILayout.clear()
        TUILayout.print_header("FINANCEIRO")
        options = [
            ("1", "Registrar Entrada/Saída"),
            ("2", "Consultar Financeiro do Cliente"),
            ("---", "Resumo"),
            ("3", "Resumo Financeiro Geral"),
            ("0", "Voltar")
        ]
        for key, label in options:
            TUILayout.print_menu_option(key, label)
        TUILayout.print_footer()
        return input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha uma opção: {Style.RESET_ALL}").strip()

    def handle_finance(self):
        while True:
            choice = self.display_finance_menu()
            if choice == '1':
                self.registrar_financeiro_ui()
                input("Pressione Enter para continuar...")
            elif choice == '2':
                self.consultar_financeiro_ui()
                input("Pressione Enter para continuar...")
            elif choice == '3':
                self.resumo_financeiro_ui()
                input("Pressione Enter para continuar...")
            elif choice == '0':
                break
            else:
                self.print_error("Opção inválida.")

    def registrar_financeiro_ui(self):
        TUILayout.clear()
        TUILayout.print_header("REGISTRAR ENTRADA/SAÍDA")
        client_name = input("  Nome ou Alias do Cliente: ").strip()
        if not client_name:
            self.print_warning("Operação cancelada.")
            return
        descricao = input("  Descrição: ").strip()
        if not descricao:
            self.print_warning("Descrição não informada.")
            return
        try:
            valor = float(input("  Valor (use . para decimal): ").strip().replace(',', '.'))
        except ValueError:
            self.print_error("Valor inválido.")
            return
        print("  Tipo: [1] Entrada | [2] Saída")
        tipo = "ENTRADA" if input("  Escolha: ").strip() == '1' else "SAIDA"
        try:
            from foton_system.modules.shared.infrastructure.config.config import Config
            from foton_system.modules.finance.application.use_cases.finance_service import FinanceService
            from foton_system.modules.finance.infrastructure.repositories.csv_finance_repository import CSVFinanceRepository
            config = Config()
            client_path = self.client_service.resolve_client_path(client_name)
            repo = CSVFinanceRepository(config=config)
            service = FinanceService(repo)
            result = service.add_entry(client_path, descricao, valor, tipo)
            self.print_success(f"\n✅ Registrado! Saldo: R$ {result.get('saldo', 0):.2f}")
        except ValueError as e:
            self.print_error(f"\n❌ {e}")
        except Exception as e:
            self.print_error(f"\n❌ Erro: {e}")

    def consultar_financeiro_ui(self):
        TUILayout.clear()
        TUILayout.print_header("CONSULTAR FINANCEIRO")
        client_name = input("  Nome ou Alias do Cliente: ").strip()
        if not client_name:
            self.print_warning("Operação cancelada.")
            return
        try:
            from foton_system.modules.shared.infrastructure.config.config import Config
            from foton_system.modules.finance.application.use_cases.finance_service import FinanceService
            from foton_system.modules.finance.infrastructure.repositories.csv_finance_repository import CSVFinanceRepository
            config = Config()
            client_path = self.client_service.resolve_client_path(client_name)
            repo = CSVFinanceRepository(config=config)
            service = FinanceService(repo)
            result = service.get_summary(client_path)
            print(f"\n  {Fore.CYAN}Resumo Financeiro: {client_path.name}{Style.RESET_ALL}")
            print(f"  {'─' * 40}")
            print(f"  ✅ Entradas: R$ {result.get('total_entradas', 0):,.2f}")
            print(f"  ❌ Saídas:   R$ {result.get('total_saidas', 0):,.2f}")
            saldo = result.get('saldo', 0)
            cor = Fore.GREEN if saldo >= 0 else Fore.RED
            print(f"  {cor}Saldo:     R$ {saldo:,.2f}{Style.RESET_ALL}")
        except ValueError as e:
            self.print_error(f"\n❌ {e}")
        except Exception as e:
            self.print_error(f"\n❌ Erro: {e}")

    def resumo_financeiro_ui(self):
        TUILayout.clear()
        TUILayout.print_header("RESUMO FINANCEIRO GERAL")
        try:
            from foton_system.modules.shared.infrastructure.config.config import Config
            from foton_system.modules.finance.application.use_cases.finance_service import FinanceService
            from foton_system.modules.finance.infrastructure.repositories.csv_finance_repository import CSVFinanceRepository
            from foton_system.modules.shared.infrastructure.services.environment_porter import get_porter
            config = Config()
            porter = get_porter()
            clients_dir = config.base_pasta_clientes
            ignored = set(config.ignored_folders + ['.obsidian'])
            client_paths = []
            for d in sorted(clients_dir.iterdir()):
                if d.is_dir() and d.name not in ignored:
                    client_paths.append(d)
            repo = CSVFinanceRepository(config=config)
            service = FinanceService(repo)
            results = service.get_firm_summary(client_paths)
            if not results:
                self.print_warning("\n  Nenhum dado financeiro encontrado.")
                return
            total_entradas = sum(r.get('income', 0) for r in results)
            total_saidas = sum(r.get('expense', 0) for r in results)
            saldo = total_entradas - total_saidas
            print(f"  {'─' * 50}")
            print(f"  📊 Resumo Geral ({len(results)} cliente(s))")
            print(f"  {'─' * 50}")
            for r in results:
                s = r.get('balance', 0)
                c = Fore.GREEN if s >= 0 else Fore.RED
                print(f"  {r.get('name', '?'):20s}  E: R$ {r.get('income', 0):>8.2f}  "
                      f"S: R$ {r.get('expense', 0):>8.2f}  "
                      f"{c}Saldo: R$ {s:>8.2f}{Style.RESET_ALL}")
            print(f"  {'─' * 50}")
            cor = Fore.GREEN if saldo >= 0 else Fore.RED
            print(f"  TOTAL{'':18s}  E: R$ {total_entradas:>8.2f}  "
                  f"S: R$ {total_saidas:>8.2f}  "
                  f"{cor}Saldo: R$ {saldo:>8.2f}{Style.RESET_ALL}")
        except Exception as e:
            self.print_error(f"\n❌ Erro: {e}")

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
        TUILayout.print_header("CADASTRAR CLIENTE")
        print("\n  Preencha os dados básicos:\n")
        nome = input("  Nome do Cliente: ")
        if not nome:
            self.print_warning("Operação cancelada.")
            return
        alias = input("  Alias (Apelido): ")
        nif = input("  NIF/CPF (opcional): ")
        email = input("  Email (opcional): ")
        # Telefone input may not be provided in tests; handle gracefully
        try:
            telefone = input("  Telefone (opcional): ")
        except StopIteration:
            telefone = ""
        
        from foton_system.modules.clients.application.use_cases.client_validation import normalize_client_name
        normalized = normalize_client_name(nome)
        
        # Verificação de duplicata (pipeline seguro)
        try:
            exists = self.client_service.resolve_client_path(normalized)
            self.print_warning(f"\n⚠️ Já existe um cliente similar: {exists.name}")
            if input("  Deseja continuar mesmo assim? (S/N): ").upper() != 'S':
                self.print_warning("Operação cancelada.")
                return
        except ValueError:
            pass  # Cliente não encontrado, seguro prosseguir
        
        # Verificação de duplicata de NIF
        if nif:
            try:
                df = self.client_repo.get_clients_dataframe()
                nif_match = df[df['NIF'].astype(str).str.strip() == nif.strip()]
                if not nif_match.empty:
                    existing_name = nif_match.iloc[0].get('NomeCliente', 'desconhecido')
                    self.print_warning(f"\n⚠️ NIF já cadastrado para: {existing_name}")
                    if input("  Deseja continuar mesmo assim? (S/N): ").upper() != 'S':
                        self.print_warning("Operação cancelada.")
                        return
            except Exception:
                pass
        
        try:
            result = self.client_service.create_client(nome, tax_id=nif, email=email, phone=telefone, alias=alias)
            self.print_success(f"\n✅ Cliente criado! Código: {result.codigo}")
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
