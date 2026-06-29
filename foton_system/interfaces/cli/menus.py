import sys
import os
import time
from pathlib import Path
from typing import Optional
from colorama import init, Fore, Style

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
from foton_system.interfaces.cli.menus_clients import MenuClientsHandler
from foton_system.interfaces.cli.menus_finance import MenuFinanceHandler
from foton_system.interfaces.cli.menus_docs import MenuDocsHandler
from foton_system.interfaces.cli.menus_config import MenuConfigHandler
from foton_system.interfaces.cli.command_parser import parse_command
from foton_system.core.ops.session_tracker import increment_operations

init(autoreset=True)

logger = setup_logger()


class MenuSystem:
    def __init__(self, ui_provider: Optional[UIProvider] = None):
        self.porter = get_porter()
        self.ui = ui_provider or get_ui_provider('auto')

        self.client_repo = ExcelClientRepository()
        self.client_service = ClientService(self.client_repo)

        self.docx_adapter = PythonDocxAdapter()
        self.pptx_adapter = PythonPPTXAdapter()
        self.document_service = DocumentService(self.docx_adapter, self.pptx_adapter)

        self.tip_service = TipService()

        self._ensure_database_exists()

        self._clients_handler = MenuClientsHandler(self)
        self._finance_handler = MenuFinanceHandler(self)
        self._docs_handler = MenuDocsHandler(self)
        self._config_handler = MenuConfigHandler(self)

    def __getattr__(self, name):
        try:
            handlers = (self._clients_handler, self._finance_handler, self._docs_handler, self._config_handler)
        except AttributeError:
            raise AttributeError(f"'MenuSystem' object has no attribute '{name}'")
        for handler in handlers:
            if hasattr(handler, name):
                return getattr(handler, name)
        raise AttributeError(f"'MenuSystem' object has no attribute '{name}'")

    def _get_logger(self):
        return logger

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

    def confirm_action(self, message: str, dangerous: bool = False) -> bool:
        if dangerous:
            self.print_warning(f"  ⚠ {message} (S/N): ")
        else:
            self.print_info(f"  {message} (S/N): ")
        result = input().strip().upper()
        return result == 'S'

    def _ensure_database_exists(self):
        from foton_system.modules.shared.infrastructure.config.config import Config
        import pandas as pd

        try:
            config = Config()
            db_path = config.get('caminho_baseDados')

            if not db_path:
                return

            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)

            if not os.path.exists(db_path):
                self.print_warning(f"Base de dados nao encontrada em: {db_path}")
                self.print_warning("Inicializando nova base de dados com estrutura completa...")

                with pd.ExcelWriter(db_path, engine='openpyxl') as writer:
                    df_clientes = pd.DataFrame(columns=[
                        'ID', 'NomeCliente', 'Alias', 'TelefoneCliente', 'Email',
                        'CPF_CNPJ', 'Endereco', 'CidadeProposta', 'EstadoCivil', 'Profissao'
                    ])
                    df_clientes.to_excel(writer, sheet_name='baseClientes', index=False)

                    df_servicos = pd.DataFrame(columns=[
                        'ID', 'AliasCliente', 'Alias', 'CodServico', 'Modalidade', 'Ano',
                        'Demanda', 'AreaTotal', 'AreaCoberta', 'AreaDescoberta',
                        'Detalhes', 'Estilo', 'Ambientes', 'ValorProposta', 'ValorContrato'
                    ])
                    df_servicos.to_excel(writer, sheet_name='baseServiços', index=False)

                self.print_success("Base de dados criada com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao verificar/criar base de dados: {e}", exc_info=True)

    def display_main_menu(self):
        TUILayout.clear()
        TUILayout.print_header("FOTON SYSTEM")

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

        active_options = [(k, l) for k, l, available in all_options if available]

        for key, label in active_options:
            TUILayout.print_menu_option(key, label)

        try:
            tip = self.tip_service.get_random_tip("GERAL")
            TUILayout.print_tip(tip, "DICA")
        except Exception:
            pass

        TUILayout.print_footer()
        return input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha uma opcao: {Style.RESET_ALL}").strip()

    def run(self):
        try:
            while True:
                choice = self.display_main_menu()
                cmd = parse_command(choice)

                if cmd['action'] == 'exit':
                    print("Saindo...")
                    sys.exit()
                elif cmd['action'] == 'help':
                    self.print_info("  Ajuda: Digite o numero da opcao ou 'q' para sair, 'h' para ajuda")
                    input("  Pressione Enter para continuar...")
                    continue
                elif cmd['action'] == 'home':
                    continue
                elif cmd['action'] == 'global_search':
                    increment_operations()
                    self.global_search_ui()
                    continue
                elif cmd['action'] == 'search':
                    increment_operations()
                    self.print_info(f"  Buscando por '{cmd['term']}'...")
                    self.global_search_ui(term=cmd['term'])
                    continue
                elif cmd['action'] == 'numeric':
                    val = cmd['value']
                    if val == 1:
                        increment_operations()
                        self.handle_clients()
                    elif val == 2:
                        increment_operations()
                        self.handle_services()
                    elif val == 3:
                        increment_operations()
                        self.handle_webview_interface()
                    elif val == 4:
                        increment_operations()
                        self.handle_documents()
                    elif val == 5:
                        increment_operations()
                        self.handle_finance()
                    elif val == 6:
                        increment_operations()
                        self.handle_productivity()
                    elif val == 7:
                        increment_operations()
                        self.handle_settings()
                    elif val == 8:
                        increment_operations()
                        self.handle_installation()
                    elif val == 9:
                        increment_operations()
                        self.handle_watcher()
                    elif val == 0:
                        print("Saindo...")
                        sys.exit()
                    else:
                        self.print_error("Opção inválida.")
                else:
                    self.print_error("Opção inválida.")
        except KeyboardInterrupt:
            print("\n")
            self.print_warning("Interrupcao detectada. Encerrando o sistema com seguranca...")
            sys.exit()

    def global_search_ui(self, term=None):
        TUILayout.clear()
        TUILayout.print_header("BUSCA GLOBAL")
        if term is None:
            query = input("\n  Digite o termo de busca: ").strip()
        else:
            query = term
        if not query:
            self.print_warning("Termo vazio.")
            return
        _start = time.perf_counter()
        try:
            df_clients = self.client_service.repository.get_clients_dataframe()
            df_services = self.client_service.repository.get_services_dataframe()

            client_results = []
            for _, row in df_clients.iterrows():
                if query.lower() in str(row.get('NomeCliente', '')).lower() or \
                   query.lower() in str(row.get('Alias', '')).lower() or \
                   query.lower() in str(row.get('CodCliente', '')).lower() or \
                   query.lower() in str(row.get('CPF_CNPJ', '')).lower():
                    client_results.append(row)

            service_results = []
            for _, row in df_services.iterrows():
                if query.lower() in str(row.get('Alias', '')).lower():
                    service_results.append(f"  Servico: {row.get('AliasCliente')}/{row.get('Alias')}")

            if client_results or service_results:
                print(f"\n  Resultados para '{query}':\n")
                for i, row in enumerate(client_results, start=1):
                    print(f"  {Fore.YELLOW}{i}.{Style.RESET_ALL} Cliente: {row.get('Alias')} ({row.get('NomeCliente')})")
                for r in service_results:
                    print(r)

                if client_results:
                    choice = input("\n  Digite o numero para abrir a ficha (ENTER para voltar): ").strip()
                    if choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(client_results):
                            selected = client_results[idx]
                            self.read_client_info_ui(selected.get('Alias', '') or '')
            else:
                print(f"\n  Nenhum resultado para '{query}'.")
            logger.info(f"perf: global_search_ui('{query}') completed in {time.perf_counter() - _start:.3f}s")
        except Exception as e:
            self.print_error(f"\n  Erro: {e}")

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
        print("\n  Padrao: 02-{COD}_DOC_PC_{VER}_{REV}_{DESC}.md")
        cod = input("  Codigo (COD) [ex: 001]: ")
        if not cod:
            self.print_error("  Codigo e obrigatorio.")
            return None

        ver = input("  Versao (VER) [00]: ") or "00"
        rev = input("  Revisao (REV) [R00]: ") or "R00"
        desc = input("  Descrição (DESC) [PROPOSTA]: ") or "PROPOSTA"

        return self.document_service.create_custom_data_file(client_path, cod, ver, rev, desc)
