from pathlib import Path
from colorama import Fore, Style
from foton_system.interfaces.cli.views.tui_layout import TUILayout
from foton_system.interfaces.cli.helpers.error_suggestions import format_error_with_suggestion


class MenuDocsHandler:
    def __init__(self, menu):
        self.menu = menu

    def display_documents_menu(self):
        TUILayout.clear()
        TUILayout.print_header("DOCUMENTOS")
        self.menu.print_breadcrumb(["Documentos"])
        options = [
            ("1", "Gerar Proposta (PPTX)"),
            ("2", "Gerar Contrato (DOCX)"),
            ("3", "Validar Template (Pre-voo)"),
            ("4", "Histórico de Documentos"),
            ("0", "Voltar")
        ]
        for key, label in options:
            TUILayout.print_menu_option(key, label)
        try:
            tip = self.menu.tip_service.get_random_tip("FORMATACAO")
            TUILayout.print_tip(tip, "DOCS")
        except Exception:
            pass
        TUILayout.print_footer()
        return input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha uma opcao: {Style.RESET_ALL}").strip()

    def handle_documents(self):
        while True:
            choice = self.menu.display_documents_menu()
            if choice == '1':
                self.menu.generate_document_ui('pptx')
            elif choice == '2':
                self.menu.generate_document_ui('docx')
            elif choice == '3':
                self.menu.validate_template_ui()
            elif choice == '4':
                self.history_documents_ui()
            elif choice in ('0', 'b', 'B'):
                break
            else:
                self.menu.print_error("Opção inválida.")

    def handle_webview_interface(self):
        from pathlib import Path
        TUILayout.clear()
        TUILayout.print_header("PREENCHIMENTO DE FICHA")
        data_file = self.menu.ui.select_file("Selecione o Arquivo de Dados (.md)", extensions=[".md"])
        if not data_file:
            self.menu.print_warning("Nenhum arquivo selecionado.")
            return
        data_path = Path(data_file)
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                content = f.read()

            def save_fn(new_content):
                try:
                    with open(data_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    return True
                except Exception as e:
                    logger = self.menu._get_logger()
                    logger.error(f"Erro ao salvar: {e}")
                    return False

            filler = self.menu.porter.get_form_filler()
            from foton_system.modules.shared.infrastructure.services.environment_porter import SystemProfile
            if self.menu.porter.profile == SystemProfile.SERVER_HEADLESS:
                filler.open_form(content, save_fn)
                input("Pressione Enter para continuar...")
                return
            print(f"\n{Fore.YELLOW}Escolha o modo de preenchimento:{Style.RESET_ALL}")
            print("  [1] Terminal (Nativo)")
            print("  [2] Interface Rica (Visual/Web)")
            print("  [0] Cancelar")
            sub_choice = input(f"\n{Fore.YELLOW}>> Escolha: {Style.RESET_ALL}").strip()
            if sub_choice == '1':
                from foton_system.modules.documents.application.use_cases.tui_form_filler_use_case import TUIFormFillerUseCase
                tui_filler = TUIFormFillerUseCase(data_path)
                if tui_filler.execute():
                    self.menu.print_success("\n  Ficha atualizada com sucesso via Terminal!")
                    input("Pressione Enter para continuar...")
            elif sub_choice == '2':
                print(f"Iniciando interface para: {data_path.name}")
                if not filler.open_form(content, save_fn):
                    self.menu.print_error("Falha ao abrir interface visual.")
                    input("Enter...")
            else:
                self.menu.print_warning("Operacao cancelada.")
        except Exception as e:
            self.menu.print_error(f"Erro no pipeline de interface: {format_error_with_suggestion(e)}")
            input("Pressione Enter para voltar...")

    def generate_document_ui(self, doc_type):
        from foton_system.modules.shared.infrastructure.config.config import Config
        from pathlib import Path
        TUILayout.clear()
        TUILayout.print_header(f"GERAR DOCUMENTO ({doc_type.upper()})")
        print("\n  Selecione a pasta do cliente...")
        client_folder = self.menu.ui.select_directory("Selecione a Pasta do Cliente")
        if not client_folder:
            self.menu.print_warning("  Operacao cancelada.")
            return
        client_path = Path(client_folder)
        data_files = self.menu.document_service.list_client_data_files(client_path)
        selected_file = None
        if data_files:
            print("\n  Arquivos de dados encontrados:")
            for i, f in enumerate(data_files):
                print(f"  {i + 1}. {f.name}")
            print(f"  {len(data_files) + 1}. Criar novo arquivo")
            try:
                choice = int(input("\n  Escolha uma opcao: "))
                if 1 <= choice <= len(data_files):
                    selected_file = data_files[choice - 1]
                elif choice == len(data_files) + 1:
                    selected_file = self.menu._create_new_data_file_ui(client_path)
                else:
                    self.menu.print_error("  Opção inválida.")
                    return
            except ValueError:
                self.menu.print_error("  Entrada inválida.")
                return
        else:
            self.menu.print_warning("\n  Nenhum arquivo de dados encontrado.")
            create = input("  Deseja criar um novo arquivo? (S/N): ").upper()
            if create == 'S':
                selected_file = self.menu._create_new_data_file_ui(client_path)
            else:
                return
        if not selected_file:
            return
        templates = self.menu.document_service.list_templates(doc_type)
        if not templates:
            self.menu.print_warning("  Nenhum template encontrado.")
            return
        print("\n  Selecione o Template:")
        template_name = self.menu._select_from_list(templates)
        if not template_name:
            return
        template_path = Config().templates_path / template_name
        default_output = f"Proposta_{client_path.name}"
        output_name = input(f"\n  Nome de saida (padrao: {default_output}): ") or default_output
        if doc_type == 'pptx' and not output_name.endswith('.pptx'):
            output_name += '.pptx'
        elif doc_type == 'docx' and not output_name.endswith('.docx'):
            output_name += '.docx'
        output_path = client_path / output_name
        try:
            self.menu.document_service.generate_document(str(template_path), str(selected_file), str(output_path), doc_type)
            self.menu.print_success(f"\n  Sucesso! Gerado em: {output_path}")
            self.menu.ui.open_folder(client_path)
            input("\nPressione Enter para continuar...")
        except Exception as e:
            self.menu.print_error(f"\n  Erro ao gerar: {format_error_with_suggestion(e)}")
            input("\nPressione Enter para continuar...")

    def validate_template_ui(self):
        from foton_system.modules.shared.infrastructure.config.config import Config
        from pathlib import Path
        TUILayout.clear()
        TUILayout.print_header("VALIDAR TEMPLATE")
        print("\n  Selecione a pasta do cliente...")
        client_folder = self.menu.ui.select_directory("Selecione a Pasta")
        if not client_folder:
            return
        client_path = Path(client_folder)
        data_files = self.menu.document_service.list_client_data_files(client_path)
        if not data_files:
            self.menu.print_warning("  Nenhum arquivo INFO encontrado.")
            return
        print("\n  Arquivos disponiveis:")
        for i, f in enumerate(data_files):
            print(f"  {i+1}. {f.name}")
        try:
            idx = int(input("\n  Escolha: ")) - 1
            selected_file = data_files[idx]
        except (ValueError, IndexError):
            return
        print("\n  Tipo: [1] PPTX | [2] DOCX")
        doc_type = 'pptx' if input("  Escolha: ") == '1' else 'docx'
        templates = self.menu.document_service.list_templates(doc_type)
        print("\n  Templates:")
        template_name = self.menu._select_from_list(templates)
        if not template_name:
            return
        template_path = Config().templates_path / template_name
        missing = self.menu.document_service.validate_template_keys(str(template_path), str(selected_file), doc_type)
        if not missing:
            self.menu.print_success("\n  TUDO PRONTO! Variaveis validadas.")
        else:
            self.menu.print_warning(f"\n  FALTANDO {len(missing)} VARIAVEIS:")
            for k in missing:
                print(f"    {k}")
        input("\nPressione Enter para voltar...")

    def history_documents_ui(self):
        from pathlib import Path
        TUILayout.clear()
        TUILayout.print_header("HISTÓRICO DE DOCUMENTOS")
        print("\n  Selecione a pasta do cliente...")
        client_folder = self.menu.ui.select_directory("Selecione a Pasta do Cliente")
        if not client_folder:
            self.menu.print_warning("  Operação cancelada.")
            return
        client_path = Path(client_folder)
        jsonl_path = client_path / 'historico_documentos.jsonl'
        if not jsonl_path.exists():
            self.menu.print_warning("  Nenhum histórico encontrado para este cliente.")
            input("\nPressione Enter para voltar...")
            return
        try:
            import json
            entries = []
            with open(jsonl_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
            entries.reverse()
            if not entries:
                self.menu.print_warning("  Nenhum histórico encontrado.")
                input("\nPressione Enter para voltar...")
                return
            self.menu.print_success(f"  {len(entries)} registro(s) encontrado(s):\n")
            for i, e in enumerate(entries[:20], 1):
                status_icon = "✅" if e.get('status') == 'sucesso' else "❌"
                versao = e.get('versao', 1)
                data_hora = e.get('data_hora', '?')[:19]
                nome = e.get('nome_arquivo', '?')
                print(f"  {i}. {status_icon} [{data_hora}] {nome} (v{versao})")
            if len(entries) > 20:
                self.menu.print_warning(f"  ... e mais {len(entries) - 20} registro(s).")
        except Exception as ex:
            self.menu.print_error(f"  Erro ao ler histórico: {ex}")
        input("\nPressione Enter para voltar...")
