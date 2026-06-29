import os
import time
from pathlib import Path
from colorama import Fore, Style
from foton_system.interfaces.cli.views.tui_layout import TUILayout


class MenuClientsHandler:
    def __init__(self, menu):
        self.menu = menu

    def handle_clients(self):
        while True:
            choice = self.menu.display_clients_menu()
            if choice == '1':
                self.menu.create_client_ui()
                input("Pressione Enter para continuar...")
            elif choice == '2':
                self.menu.read_client_info_ui()
                input("Pressione Enter para continuar...")
            elif choice == '3':
                self.menu.update_client_info_ui()
                input("Pressione Enter para continuar...")
            elif choice == '4':
                self.menu.fill_missing_codes_ui()
                input("Pressione Enter para continuar...")
            elif choice == '5':
                from foton_system.modules.clients.application.use_cases.pipeline_sync import pipeline_sincronizacao, format_sync_report
                report = pipeline_sincronizacao('pastas_to_db', dry_run=False)
                self.menu.print_info(format_sync_report(report))
                input("Pressione Enter para continuar...")
            elif choice == '6':
                from foton_system.modules.clients.application.use_cases.pipeline_sync import pipeline_sincronizacao, format_sync_report
                report = pipeline_sincronizacao('db_to_pastas', dry_run=False)
                self.menu.print_info(format_sync_report(report))
                input("Pressione Enter para continuar...")
            elif choice == '7':
                self.menu.pipeline_sync_ui()
                input("Pressione Enter para continuar...")
            elif choice == '8':
                self.menu.list_all_clients_ui()
            elif choice == '9':
                self.menu.search_client_ui()
                input("Pressione Enter para continuar...")
            elif choice == '10':
                self.menu.handle_client_servicos_menu()
                input("Pressione Enter para continuar...")
            elif choice == '11':
                self.menu.handle_client_sync_menu()
            elif choice == '12':
                self.menu.remove_client_ui()
                input("Pressione Enter para continuar...")
            elif choice == '13':
                self.menu.restore_client_ui()
                input("Pressione Enter para continuar...")
            elif choice in ('0', 'b', 'B'):
                break
            else:
                self.menu.print_error("Opção inválida.")

    def display_clients_menu(self):
        TUILayout.clear()
        TUILayout.print_header("GERENCIAR CLIENTES")
        self.menu.print_breadcrumb(["Clientes"])
        options = [
            ("---", "Cadastro"),
            ("1", "Cadastrar Cliente (com verificacao)"),
            ("2", "Ler Ficha (INFO) do Cliente"),
            ("3", "Atualizar Ficha do Cliente"),
            ("4", "Preencher Codigos Faltantes"),
            ("---", "Manutenção"),
            ("5", "Sincronizar Base (Pastas -> DB)"),
            ("6", "Sincronizar Pastas (DB -> Pastas)"),
            ("7", "Pipeline Sincronização (Unificado)"),
            ("8", "Listar Todos os Clientes"),
            ("9", "Buscar Cliente"),
            ("---", "Serviços"),
            ("10", "Serviços do Cliente"),
            ("11", "Sincronizar Cadastro (DB <-> Arquivo)"),
            ("---", "Perigo"),
            ("12", "Remover Cliente"),
            ("13", "Restaurar Cliente"),
            ("0", "Voltar")
        ]
        for key, label in options:
            TUILayout.print_menu_option(key, label)
        try:
            tip = self.menu.tip_service.get_random_tip("SSOT")
            TUILayout.print_tip(tip, "CLIENTE")
        except Exception:
            pass
        TUILayout.print_footer()
        return input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha uma opcao: {Style.RESET_ALL}").strip()

    def display_services_menu(self):
        TUILayout.clear()
        TUILayout.print_header("GERENCIAR SERVIÇOS")
        self.menu.print_breadcrumb(["Serviços"])
        options = [
            ("1", "Sincronizar Base (Pastas -> DB)"),
            ("2", "Sincronizar Pastas (DB -> Pastas) [Todos]"),
            ("3", "Sincronizar Pastas (DB -> Pastas) [Por Cliente]"),
            ("4", "Sincronizar Cadastro (DB <-> Arquivo)"),
            ("0", "Voltar")
        ]
        for key, label in options:
            TUILayout.print_menu_option(key, label)
        try:
            tip = self.menu.tip_service.get_random_tip("PRODUTIVIDADE")
            TUILayout.print_tip(tip, "SERVICO")
        except Exception:
            pass
        TUILayout.print_footer()
        return input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha uma opcao: {Style.RESET_ALL}").strip()

    def handle_services(self):
        while True:
            choice = self.menu.display_services_menu()
            if choice == '1':
                from foton_system.modules.clients.application.use_cases.pipeline_sync import pipeline_sincronizacao, format_sync_report
                report = pipeline_sincronizacao('pastas_to_db', dry_run=False)
                self.menu.print_info(format_sync_report(report))
                input("Pressione Enter para continuar...")
            elif choice == '2':
                from foton_system.modules.clients.application.use_cases.pipeline_sync import pipeline_sincronizacao, format_sync_report
                report = pipeline_sincronizacao('db_to_pastas', dry_run=False)
                self.menu.print_info(format_sync_report(report))
                input("Pressione Enter para continuar...")
            elif choice == '3':
                alias = input("Digite o Alias do Cliente: ").strip()
                if alias:
                    from foton_system.modules.clients.application.use_cases.pipeline_sync import pipeline_sincronizacao, format_sync_report
                    report = pipeline_sincronizacao('db_to_pastas', dry_run=False)
                    self.menu.print_info(format_sync_report(report))
                input("Pressione Enter para continuar...")
            elif choice == '4':
                self.menu.handle_service_sync_menu()
            elif choice in ('0', 'b', 'B'):
                break
            else:
                self.menu.print_error("Opção inválida.")

    def read_client_info_ui(self, client_name=None):
        TUILayout.clear()
        TUILayout.print_header("LER FICHA DO CLIENTE")
        if not client_name:
            client_name = input("\n  Nome ou Alias do Cliente: ").strip()
            if not client_name:
                self.menu.print_warning("Operacao cancelada.")
                return
        try:
            result = self.menu.client_service.read_client_info(client_name)
            print(f"\n  {Fore.CYAN}Arquivo: {result['filename']}{Style.RESET_ALL}")
            print(f"  {Fore.WHITE}{chr(9472) * 60}{Style.RESET_ALL}")
            print(result['content'])
        except ValueError as e:
            self.menu.print_error(f"\n  {e}")
        except Exception as e:
            self.menu.print_error(f"\n  Erro: {e}")

    def update_client_info_ui(self):
        TUILayout.clear()
        TUILayout.print_header("ATUALIZAR FICHA DO CLIENTE")
        client_name = input("\n  Nome ou Alias do Cliente: ").strip()
        if not client_name:
            self.menu.print_warning("Operacao cancelada.")
            return
        secao = input("  Secao (ex: DADOS DO CLIENTE - PROPOSTA): ").strip()
        if not secao:
            self.menu.print_warning("Secao nao informada.")
            return
        print("  Digite o conteudo (linha em branco para finalizar):")
        linhas = []
        while True:
            linha = input("  > ")
            if not linha:
                break
            linhas.append(linha)
        conteudo = "\n".join(linhas)
        if not conteudo:
            self.menu.print_warning("Conteudo vazio.")
            return
        try:
            backup = self.menu.client_service.update_client_info(client_name, secao, conteudo)
            self.menu.print_success(f"\n  Ficha atualizada! Backup: {backup}")
        except ValueError as e:
            self.menu.print_error(f"\n  {e}")
        except Exception as e:
            self.menu.print_error(f"\n  Erro: {e}")

    def fill_missing_codes_ui(self):
        TUILayout.clear()
        TUILayout.print_header("PREENCHER CODIGOS FALTANTES")
        print(f"\n  {Fore.YELLOW}Isso vai varrer o banco de dados e gerar codigos{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}para todos os registros que ainda nao possuem{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}CodCliente ou CodServico.{Style.RESET_ALL}\n")
        if not self.menu.confirm_action("Prosseguir?"):
            self.menu.print_warning("Operacao cancelada.")
            return
        try:
            result = self.menu.client_service.fill_missing_codes()
            clientes = result['clientes_alterados']
            servicos = result['servicos_alterados']
            if clientes:
                self.menu.print_success(f"\n  {clientes} cliente(s) receberam codigo!")
            if servicos:
                self.menu.print_success(f"  {servicos} servico(s) receberam codigo!")
            if not clientes and not servicos:
                self.menu.print_success("\n  Nenhum codigo faltante encontrado. Todos os registros ja possuem codigo.")
        except Exception as e:
            self.menu.print_error(f"\n  Erro: {e}")

    def remove_client_ui(self):
        TUILayout.clear()
        TUILayout.print_header("REMOVER CLIENTE")
        print(f"\n  {Fore.YELLOW}  ATENCAO: Esta operacao marca o cliente como DELETADO.{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}    O cliente continuara visivel na lista mas nao aparecera em buscas.{Style.RESET_ALL}\n")
        client_name = input("  Nome ou Alias do Cliente: ").strip()
        if not client_name:
            self.menu.print_warning("Operacao cancelada.")
            return
        if not self.menu.confirm_action(f"Confirmar remocao de '{client_name}'?", dangerous=True):
            self.menu.print_warning("Operacao cancelada.")
            return
        try:
            result = self.menu.client_service.soft_delete_client(client_name)
            if result["success"]:
                self.menu.print_success(f"\n  {result['message']}")
            else:
                self.menu.print_error(f"\n  {result['error']}")
        except Exception as e:
            self.menu.print_error(f"\n  Erro: {e}")

    def restore_client_ui(self):
        try:
            deleted = self.menu.client_service.get_deleted_clients()
            if not deleted:
                TUILayout.clear()
                TUILayout.print_header("RESTAURAR CLIENTE")
                self.menu.print_warning("\n  Nenhum cliente deletado encontrado.")
                return
            TUILayout.paginate_items(
                deleted,
                render_item=lambda c, i: print(f"  {i}. {c.get('Alias', '?')} ({c.get('NomeCliente', '?')})"),
                header_title="RESTAURAR CLIENTE",
                empty_msg="Nenhum cliente deletado encontrado.",
            )
            client_name = input("\n  Alias do cliente a restaurar: ").strip()
            if not client_name:
                self.menu.print_warning("Operacao cancelada.")
                return
            if not self.menu.confirm_action(f"Restaurar '{client_name}'?"):
                self.menu.print_warning("Operacao cancelada.")
                return
            result = self.menu.client_service.restore_client(client_name)
            if result["success"]:
                self.menu.print_success(f"\n  {result['message']}")
            else:
                self.menu.print_error(f"\n  {result['error']}")
        except Exception as e:
            self.menu.print_error(f"\n  Erro: {e}")

    def pipeline_sync_ui(self):
        TUILayout.clear()
        TUILayout.print_header("PIPELINE SINCRONIZAÇÃO")
        print("\n  Direcoes disponiveis:")
        print("  1. pastas_to_db (descobrir novas pastas)")
        print("  2. db_to_pastas (criar pastas faltantes)")
        print("  3. bidir (ambas - padrao)")
        direcao_map = {'1': 'pastas_to_db', '2': 'db_to_pastas', '3': 'bidir'}
        choice = input("\n  Escolha [3]: ").strip() or '3'
        direcao = direcao_map.get(choice, 'bidir')
        try:
            from foton_system.modules.clients.application.use_cases.pipeline_sync import pipeline_sincronizacao, format_sync_report
            report = pipeline_sincronizacao(direcao)
            print(f"\n{format_sync_report(report)}")
        except Exception as e:
            self.menu.print_error(f"\n  Erro: {e}")

    def search_client_ui(self):
        term = input("\n  Digite o nome ou alias: ").strip().lower()
        if not term:
            self.menu.list_all_clients_ui()
            return
        self.menu.global_search_ui(term=term)

    def list_all_clients_ui(self):
        TUILayout.clear()
        TUILayout.print_header("LISTAR TODOS OS CLIENTES")
        _start = time.perf_counter()
        try:
            df = self.menu.client_repo.get_all_clients_dataframe()
            if df.empty:
                self.menu.print_warning("\nNenhum cliente cadastrado.")
                input("\n  Pressione Enter para continuar...")
                return
            rows = df.to_dict('records')
            page_size = 10
            total = len(rows)
            for start in range(0, total, page_size):
                TUILayout.clear()
                TUILayout.print_header(f"LISTAR TODOS OS CLIENTES ({total})")
                page_rows = rows[start:start + page_size]
                for i, row in enumerate(page_rows, start=start + 1):
                    cod = row.get('CodCliente', '') or ''
                    nome = row.get('NomeCliente', '') or ''
                    alias = row.get('Alias', '') or ''
                    status = row.get('Status', 'ATIVO') or 'ATIVO'
                    status_tag = f" {Fore.RED}[DELETADO]{Style.RESET_ALL}" if status == 'DELETADO' else ""
                    print(f"  {Fore.YELLOW}{i:3d}.{Style.RESET_ALL} "
                          f"{Fore.CYAN}{cod:<8}{Style.RESET_ALL} "
                          f"{Fore.WHITE}{nome:<30}{Style.RESET_ALL} "
                          f"{Fore.LIGHTBLACK_EX}{alias:<20}{Style.RESET_ALL}"
                          f"{status_tag}")
                remaining = total - (start + page_size)
                if remaining > 0:
                    input(f"\n  {Fore.CYAN}Pressione Enter para ver mais {remaining} cliente(s)...{Style.RESET_ALL}")
            logger = self.menu._get_logger()
            logger.info(f"perf: list_all_clients_ui ({total} clients) completed in {time.perf_counter() - _start:.3f}s")
            input(f"\n  {Fore.GREEN}Fim da lista.{Style.RESET_ALL} Pressione Enter para continuar...")
        except Exception as e:
            self.menu.print_error(f"\n  Erro ao listar clientes: {e}")
            input("\n  Pressione Enter para continuar...")

    def handle_client_servicos_menu(self):
        while True:
            TUILayout.clear()
            TUILayout.print_header("SERVIÇOS DO CLIENTE")
            self.menu.print_breadcrumb(["Clientes", "Serviços"])
            TUILayout.print_menu_option("1", "Listar Serviços")
            TUILayout.print_menu_option("2", "Criar Estrutura de Servico")
            TUILayout.print_menu_option("3", "Validar Codigos de Servico")
            TUILayout.print_menu_option("4", "Corrigir Codigos de Servico")
            TUILayout.print_menu_option("0", "Voltar")
            TUILayout.print_footer()
            sub = input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha: {Style.RESET_ALL}")
            if sub == '1':
                self.menu.list_client_servicos_ui()
                input("Pressione Enter para continuar...")
            elif sub == '2':
                self.menu.create_client_servico_ui()
                input("Pressione Enter para continuar...")
            elif sub == '3':
                self.menu.validar_codigos_servicos_ui()
                input("Pressione Enter para continuar...")
            elif sub == '4':
                self.menu.corrigir_codigos_servicos_ui()
                input("Pressione Enter para continuar...")
            elif sub in ('0', 'b', 'B'):
                break
            else:
                self.menu.print_error("Opção inválida.")

    def list_client_servicos_ui(self):
        client_name = input("\n  Nome ou Alias do Cliente: ").strip()
        if not client_name:
            self.menu.print_warning("Operacao cancelada.")
            return
        try:
            servicos = self.menu.client_service.list_service_nodes(client_name)
            if not servicos:
                TUILayout.clear()
                TUILayout.print_header("LISTAR SERVIÇOS DO CLIENTE")
                self.menu.print_warning(f"\n  Nenhum servico encontrado para '{client_name}'.")
                return
            for svc in servicos:
                svc['_subdirs'] = ', '.join(s.name for s in Path(svc['path']).iterdir() if s.is_dir())
            header = f"SERVIÇOS DE {client_name.upper()} ({len(servicos)} encontrado(s))"
            TUILayout.paginate_items(
                servicos,
                render_item=lambda svc, i: (
                    print(f"  {'  ' * svc['depth']}{i}.  {svc['name']} ({svc['file_count']} arquivo(s))"),
                    svc['_subdirs'] and print(f"  {'  ' * svc['depth']}    Subpastas: {svc['_subdirs']}")
                ),
                header_title=header,
                empty_msg=f"Nenhum servico encontrado para '{client_name}'.",
            )
        except ValueError as e:
            self.menu.print_error(f"\n  {e}")
        except Exception as e:
            self.menu.print_error(f"\n  Erro: {e}")

    def create_client_servico_ui(self):
        TUILayout.clear()
        TUILayout.print_header("CRIAR ESTRUTURA DE SERVICO")
        client_name = input("  Nome ou Alias do Cliente: ").strip()
        if not client_name:
            self.menu.print_warning("Operacao cancelada.")
            return
        service_name = input("  Nome do Servico: ").strip()
        if not service_name:
            self.menu.print_warning("Nome do servico nao informado.")
            return
        try:
            from foton_system.modules.shared.infrastructure.config.config import Config
            config = Config()
            client_path = self.menu.client_service.resolve_client_path(client_name)
            client_alias = client_path.name
            service_path = client_path / service_name
            if service_path.exists():
                self.menu.print_warning(f"\n  Ja existe uma pasta: {service_path}")
                return
            from foton_system.modules.shared.infrastructure.validators import validate_filename
            if not validate_filename(service_name):
                self.menu.print_error("Nome do servico contem caracteres invalidos.")
                return
            entry = self.menu.client_service.create_service_entry(client_alias, service_name)
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
            self.menu.print_success(f"\n  Servico '{service_name}' criado em {service_path}!")
            self.menu.print_success(f"   Codigo do servico: {cod_servico}")
        except ValueError as e:
            self.menu.print_error(f"\n  {e}")
        except Exception as e:
            self.menu.print_error(f"\n  Erro: {e}")

    def validar_codigos_servicos_ui(self):
        TUILayout.clear()
        TUILayout.print_header("VALIDAR CODIGOS DE SERVICO")
        try:
            result = self.menu.client_service.fill_missing_codes()
            if result.get('servicos_alterados'):
                self.menu.print_success(f"\n  {result['servicos_alterados']} servico(s) receberam codigo automaticamente.")
            issues = self.menu.client_service.validate_service_codes()
            if not issues:
                self.menu.print_success("\n  Todos os codigos de servico sao validos.")
                return
            n_issues = len(issues)
            self.menu.print_warning(f"\n  {n_issues} codigo(s) de servico com problema:")
            for iss in issues:
                svc_label = f"{iss['client_alias']}/{iss['service_alias']}"
                print(f"\n    [{iss['issue'].upper()}] {svc_label}")
                print(f"      Codigo: '{iss['cod_servico']}'")
                print(f"      Sugestao: {iss['suggested_fix']}")
        except Exception as e:
            self.menu.print_error(f"\n  Erro: {e}")

    def corrigir_codigos_servicos_ui(self):
        TUILayout.clear()
        TUILayout.print_header("CORRIGIR CODIGOS DE SERVICO")
        try:
            result = self.menu.client_service.fill_missing_codes()
            if result.get('servicos_alterados'):
                self.menu.print_success(f"\n  {result['servicos_alterados']} servico(s) receberam codigo automaticamente.")
            issues = self.menu.client_service.validate_service_codes()
            if not issues:
                self.menu.print_success("\n  Todos os codigos de servico ja sao validos.")
                return
            fixed = self.menu.client_service.fix_service_codes(issues)
            self.menu.print_success(f"\n  {fixed} codigo(s) de servico corrigido(s) automaticamente.")
        except Exception as e:
            self.menu.print_error(f"\n  Erro: {e}")

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
                self.menu.client_service.export_client_data()
                input("Pressione Enter para continuar...")
            elif sub == '2':
                self.menu.client_service.import_client_data()
                input("Pressione Enter para continuar...")
            elif sub in ('0', 'b', 'B'):
                break
            else:
                self.menu.print_error("Opção inválida.")

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
                self.menu.client_service.export_service_data()
                input("Pressione Enter para continuar...")
            elif sub == '2':
                self.menu.client_service.import_service_data()
                input("Pressione Enter para continuar...")
            elif sub in ('0', 'b', 'B'):
                break
            else:
                self.menu.print_error("Opção inválida.")

    def create_client_ui(self):
        TUILayout.clear()
        TUILayout.print_header("CADASTRAR CLIENTE")
        print("\n  Preencha os dados basicos:\n")
        nome = input("  Nome do Cliente: ")
        if not nome:
            self.menu.print_warning("Operacao cancelada.")
            return
        alias = input("  Alias (Apelido): ")
        nif = input("  NIF/CPF (opcional): ")
        email = input("  Email (opcional): ")
        try:
            telefone = input("  Telefone (opcional): ")
        except StopIteration:
            telefone = ""
        from foton_system.modules.clients.application.use_cases.client_validation import normalize_client_name
        normalized = normalize_client_name(nome)
        try:
            exists = self.menu.client_service.resolve_client_path(normalized)
            self.menu.print_warning(f"\n  Ja existe um cliente similar: {exists.name}")
            if input("  Deseja continuar mesmo assim? (S/N): ").upper() != 'S':
                self.menu.print_warning("Operacao cancelada.")
                return
        except ValueError:
            pass
        if nif:
            try:
                df = self.menu.client_repo.get_clients_dataframe()
                nif_match = df[df['NIF'].astype(str).str.strip() == nif.strip()]
                if not nif_match.empty:
                    existing_name = nif_match.iloc[0].get('NomeCliente', 'desconhecido')
                    self.menu.print_warning(f"\n  NIF ja cadastrado para: {existing_name}")
                    if input("  Deseja continuar mesmo assim? (S/N): ").upper() != 'S':
                        self.menu.print_warning("Operacao cancelada.")
                        return
            except Exception:
                pass
        try:
            result = self.menu.client_service.create_client(nome, tax_id=nif, email=email, phone=telefone, alias=alias)
            self.menu.print_success(f"\n  Cliente criado! Codigo: {result.codigo}")
        except ValueError as ve:
            self.menu.print_error(f"\n  Erro de Validação: {ve}")
        except Exception as e:
            self.menu.print_error(f"\n  Erro ao criar cliente: {e}")
