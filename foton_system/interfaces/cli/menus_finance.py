import os
from pathlib import Path
from colorama import Fore, Style
from foton_system.interfaces.cli.views.tui_layout import TUILayout
from foton_system.interfaces.cli.helpers.progress_tracker import ProgressTracker
from foton_system.interfaces.cli.helpers.error_suggestions import format_error_with_suggestion


class MenuFinanceHandler:
    def __init__(self, menu):
        self.menu = menu

    def display_finance_menu(self):
        TUILayout.clear()
        TUILayout.print_header("FINANCEIRO")
        self.menu.print_breadcrumb(["Financeiro"])
        options = [
            ("1", "Registrar Entrada/Saida"),
            ("2", "Consultar Financeiro do Cliente"),
            ("---", "Resumo"),
            ("3", "Resumo Financeiro Geral"),
            ("0", "Voltar")
        ]
        for key, label in options:
            TUILayout.print_menu_option(key, label)
        TUILayout.print_footer()
        return input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha uma opcao: {Style.RESET_ALL}").strip()

    def handle_finance(self):
        while True:
            choice = self.menu.display_finance_menu()
            if choice == '1':
                self.menu.registrar_financeiro_ui()
                input("Pressione Enter para continuar...")
            elif choice == '2':
                self.menu.consultar_financeiro_ui()
                input("Pressione Enter para continuar...")
            elif choice == '3':
                self.menu.resumo_financeiro_ui()
                input("Pressione Enter para continuar...")
            elif choice in ('0', 'b', 'B'):
                break
            else:
                self.menu.print_error("Opção inválida.")

    def registrar_financeiro_ui(self):
        TUILayout.clear()
        TUILayout.print_header("REGISTRAR ENTRADA/SAIDA")
        client_name = input("  Nome ou Alias do Cliente: ").strip()
        if not client_name:
            self.menu.print_warning("Operacao cancelada.")
            return
        descrição = input("  Descrição: ").strip()
        if not descrição:
            self.menu.print_warning("Descrição nao informada.")
            return
        try:
            valor = float(input("  Valor (use . para decimal): ").strip().replace(',', '.'))
        except ValueError:
            self.menu.print_error("Valor inválido.")
            return
        print("  Tipo: [1] Entrada | [2] Saida")
        tipo = "ENTRADA" if input("  Escolha: ").strip() == '1' else "SAIDA"
        try:
            from foton_system.modules.shared.infrastructure.config.config import Config
            from foton_system.modules.finance.application.use_cases.finance_service import FinanceService
            from foton_system.modules.finance.infrastructure.repositories.csv_finance_repository import CSVFinanceRepository
            config = Config()
            client_path = self.menu.client_service.resolve_client_path(client_name)
            repo = CSVFinanceRepository(config=config)
            service = FinanceService(repo)
            result = service.add_entry(client_path, descrição, valor, tipo)
            self.menu.print_success(f"\n  Registrado! Saldo: R$ {result.get('saldo', 0):.2f}")
        except ValueError as e:
            self.menu.print_error(f"\n  {e}")
        except Exception as e:
            self.menu.print_error(f"\n  {format_error_with_suggestion(e)}")

    def consultar_financeiro_ui(self):
        TUILayout.clear()
        TUILayout.print_header("CONSULTAR FINANCEIRO")
        client_name = input("  Nome ou Alias do Cliente: ").strip()
        if not client_name:
            self.menu.print_warning("Operacao cancelada.")
            return
        try:
            from foton_system.modules.shared.infrastructure.config.config import Config
            from foton_system.modules.finance.application.use_cases.finance_service import FinanceService
            from foton_system.modules.finance.infrastructure.repositories.csv_finance_repository import CSVFinanceRepository
            config = Config()
            client_path = self.menu.client_service.resolve_client_path(client_name)
            repo = CSVFinanceRepository(config=config)
            service = FinanceService(repo)
            result = service.get_summary(client_path)
            print(f"\n  {Fore.CYAN}Resumo Financeiro: {client_path.name}{Style.RESET_ALL}")
            print(f"  {'─' * 40}")
            print(f"  Entradas: R$ {result.get('total_entradas', 0):,.2f}")
            print(f"  Saidas:   R$ {result.get('total_saidas', 0):,.2f}")
            saldo = result.get('saldo', 0)
            cor = Fore.GREEN if saldo >= 0 else Fore.RED
            print(f"  {cor}Saldo:     R$ {saldo:,.2f}{Style.RESET_ALL}")
        except ValueError as e:
            self.menu.print_error(f"\n  {e}")
        except Exception as e:
            self.menu.print_error(f"\n  {format_error_with_suggestion(e)}")

    def resumo_financeiro_ui(self):
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
            _tracker = ProgressTracker(total=len(client_paths), description="Processando cliente")
            repo = CSVFinanceRepository(config=config)
            service = FinanceService(repo)
            results = service.get_firm_summary(client_paths, progress_callback=lambda c: _tracker.advance(c))
            _tracker.finish()
            if not results:
                TUILayout.clear()
                TUILayout.print_header("RESUMO FINANCEIRO GERAL")
                self.menu.print_warning("\n  Nenhum dado financeiro encontrado.")
                return
            total_entradas = sum(r.get('income', 0) for r in results)
            total_saidas = sum(r.get('expense', 0) for r in results)
            saldo = total_entradas - total_saidas

            def render_finance(r, i):
                s = r.get('balance', 0)
                c = Fore.GREEN if s >= 0 else Fore.RED
                print(f"  {i:3d}. {r.get('name', '?'):20s}  E: R$ {r.get('income', 0):>8.2f}  "
                      f"S: R$ {r.get('expense', 0):>8.2f}  "
                      f"{c}Saldo: R$ {s:>8.2f}{Style.RESET_ALL}")

            TUILayout.paginate_items(
                results,
                render_item=render_finance,
                header_title="RESUMO FINANCEIRO GERAL",
                empty_msg="Nenhum dado financeiro encontrado.",
            )
            print(f"  {'─' * 50}")
            cor = Fore.GREEN if saldo >= 0 else Fore.RED
            print(f"  TOTAL{'':18s}  E: R$ {total_entradas:>8.2f}  "
                  f"S: R$ {total_saidas:>8.2f}  "
                  f"{cor}Saldo: R$ {saldo:>8.2f}{Style.RESET_ALL}")
        except Exception as e:
            self.menu.print_error(f"\n  {format_error_with_suggestion(e)}")
