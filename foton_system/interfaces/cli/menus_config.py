import os
import sys
from colorama import Fore, Style
from foton_system.interfaces.cli.views.tui_layout import TUILayout
from foton_system.interfaces.cli.helpers.progress_tracker import ProgressTracker
from foton_system.interfaces.cli.helpers.error_suggestions import format_error_with_suggestion


class MenuConfigHandler:
    def __init__(self, menu):
        self.menu = menu

    def display_productivity_menu(self):
        TUILayout.clear()
        TUILayout.print_header("PRODUTIVIDADE")
        self.menu.print_breadcrumb(["Produtividade"])
        options = [
            ("1", "Iniciar Pomodoro"),
            ("0", "Voltar")
        ]
        for key, label in options:
            TUILayout.print_menu_option(key, label)
        try:
            tip = self.menu.tip_service.get_random_tip("GERAL")
            TUILayout.print_tip(tip, "FOCO")
        except Exception:
            pass
        TUILayout.print_footer()
        return input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha uma opcao: {Style.RESET_ALL}").strip()

    def display_settings_menu(self, config):
        TUILayout.clear()
        TUILayout.print_header("CONFIGURAÇÕES")
        self.menu.print_breadcrumb(["Configurações"])
        TUILayout.print_menu_option("1", f"Pasta Clientes: {os.path.basename(config.get('caminho_pastaClientes'))}")
        TUILayout.print_menu_option("2", f"Pasta Templates: {os.path.basename(config.get('caminho_templates'))}")
        TUILayout.print_menu_option("3", f"Base de Dados: {os.path.basename(config.get('caminho_baseDados'))}")
        TUILayout.print_menu_option("---", "Ferramentas")
        TUILayout.print_menu_option("4", "Ferramentas Administrativas")
        TUILayout.print_menu_option("5", "Abrir Pasta do Sistema (Workspace)")
        TUILayout.print_menu_option("6", "Pesquisa de Satisfação (NPS)")
        TUILayout.print_menu_option("7", "Exportar Dados de Uso")
        TUILayout.print_menu_option("---", "RAG")
        TUILayout.print_menu_option("8", "RAG / Modelo de Embedding")
        TUILayout.print_menu_option("0", "Voltar")
        try:
            tip = self.menu.tip_service.get_random_tip("SANDBOX")
            TUILayout.print_tip(tip, "CONFIG")
        except Exception:
            pass
        TUILayout.print_footer()
        return input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha uma opcao: {Style.RESET_ALL}").strip()

    def handle_productivity(self):
        while True:
            choice = self.menu.display_productivity_menu()
            if choice == '1':
                self.menu.start_pomodoro_ui()
            elif choice in ('0', 'b', 'B'):
                break
            else:
                self.menu.print_error("Opção inválida.")

    def handle_settings(self):
        from foton_system.modules.shared.infrastructure.config.config import Config
        config = Config()
        while True:
            choice = self.menu.display_settings_menu(config)
            if choice == '1':
                self.menu.update_setting_ui(config, 'caminho_pastaClientes', "Pasta de Clientes")
            elif choice == '2':
                self.menu.update_setting_ui(config, 'caminho_templates', "Pasta de Templates")
            elif choice == '3':
                self.menu.update_setting_ui(config, 'caminho_baseDados', "Arquivo de Base de Dados", is_file=True)
            elif choice == '4':
                self.menu.handle_admin_tools()
            elif choice == '5':
                self.menu._open_workspace_folder(config)
            elif choice == '6':
                self._pesquisa_nps_ui()
            elif choice == '7':
                self._exportar_dados_uso_ui()
            elif choice == '8':
                self.menu.handle_rag_config()
            elif choice in ('0', 'b', 'B'):
                break
            else:
                self.menu.print_error("Opção inválida.")

    def update_setting_ui(self, config, key, title, is_file=False):
        print(f"\nSelecione o novo local para: {title}")
        if is_file:
            path = self.menu.ui.select_file(f"Selecione: {title}")
        else:
            path = self.menu.ui.select_directory(f"Selecione: {title}")
        if path:
            path = os.path.normpath(str(path))
            config.set(key, path)
            config.save()
            self.menu.print_success(f"Configuracao atualizada com sucesso!\nNovo valor: {path}")
            input("Pressione Enter para continuar...")
        else:
            self.menu.print_warning("Operacao cancelada.")
            input("Pressione Enter para continuar...")

    def _pesquisa_nps_ui(self):
        from foton_system.core.ops.session_tracker import get_current_session
        from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService
        import json
        from datetime import datetime
        TUILayout.clear()
        TUILayout.print_header("PESQUISA DE SATISFAÇÃO (NPS)")
        print(f"\n  De 0 a 10, o quanto você recomendaria o Foton System")
        print(f"  para outro arquiteto ou engenheiro?")
        print()
        raw = input(f"{Fore.CYAN}  Nota (0-10): {Style.RESET_ALL}").strip()
        try:
            score = int(raw)
            if score < 0 or score > 10:
                raise ValueError
        except (ValueError, TypeError):
            self.menu.print_error("  Nota inválida. Digite um número entre 0 e 10.")
            input("\n  Pressione Enter para continuar...")
            return
        if score >= 9:
            classification = "Promotor"
        elif score >= 7:
            classification = "Neutro"
        else:
            classification = "Detrator"
        print("\n  Comentário ou sugestão? (Enter para pular)")
        comment_lines = []
        first_line = input().strip()
        if first_line:
            comment_lines.append(first_line)
            while True:
                line = input()
                if not line:
                    break
                comment_lines.append(line)
        comment = "\n".join(comment_lines)
        config_dir = BootstrapService.get_user_config_dir()
        session_count = 0
        operation_count = 0
        session_file = config_dir / "session.json"
        if session_file.exists():
            try:
                persisted = json.loads(session_file.read_text(encoding="utf-8"))
                session_count = persisted.get("total_sessoes_all_time", 0)
                operation_count = persisted.get("total_operacoes_all_time", 0)
            except (json.JSONDecodeError, OSError):
                pass
        current = get_current_session()
        session_id = current.session_id if current else ""
        interface = current.interface if current else ""
        record = {
            "timestamp": datetime.now().isoformat(),
            "score": score,
            "classification": classification,
            "comentario": comment,
            "session_count": session_count,
            "operation_count": operation_count,
            "session_id": session_id,
            "interface": interface,
        }
        try:
            nps_file = config_dir / "nps_responses.jsonl"
            with open(nps_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            scores = []
            all_responses = []
            if nps_file.exists():
                with open(nps_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                data = json.loads(line)
                                scores.append(data["score"])
                                all_responses.append(data)
                            except Exception:
                                pass
            avg = sum(scores) / len(scores) if scores else score
            print()
            TUILayout.print_menu_option("+", f"Sua nota: {score}")
            TUILayout.print_menu_option("+", f"Média atual: {avg:.1f} ({len(scores)} respostas)")
            if len(scores) >= 4:
                last_3_avg = sum(scores[-3:]) / 3
                prev = scores[-6:-3] if len(scores) >= 6 else scores[:-3]
                prev_avg = sum(prev) / len(prev) if prev else 0
                diff = last_3_avg - prev_avg
                if diff > 0.5:
                    trend = "📈"
                elif diff < -0.5:
                    trend = "📉"
                else:
                    trend = "➡️"
            else:
                trend = "➡️"
            TUILayout.print_menu_option("+", f"Tendência: {trend}")
            last_5 = all_responses[-5:]
            if last_5 and len(scores) > 1:
                print("\n  Últimas avaliações:")
                for i, r in enumerate(reversed(last_5), 1):
                    ts = r.get("timestamp", "")[:10]
                    s = r.get("score", "?")
                    print(f"  [{i}] {ts} — Nota: {s}")
            print()
            print("  Exportar para Email? (S/N)")
            if input().upper() == 'S':
                zip_path = self._exportar_nps_zip()
                if zip_path:
                    self.menu.print_success(f"  Arquivo gerado: {zip_path}")
                    print("  Envie o arquivo para contato@mundoaec.com")
            print()
            self.menu.print_success("  Obrigado pelo feedback!")
        except Exception as e:
            self.menu.print_error(f"  Erro ao salvar: {format_error_with_suggestion(e)}")
        input("\n  Pressione Enter para continuar...")

    # @rule: RULE-UX-9.2 — Exportação para email (.zip local + instrução)
    # @rule: RULE-TELEMETRY-1.5 — Exportar Dados de Uso
    def _exportar_nps_zip(self):
        import json, os, zipfile, shutil, tempfile, datetime
        from pathlib import Path
        from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService
        config_dir = BootstrapService.get_user_config_dir()
        desktop = Path.home() / "Desktop"
        desktop.mkdir(exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"foton_dados_uso_{ts}"
        zip_path = desktop / zip_name
        nps_file = config_dir / "nps_responses.jsonl"
        report_lines = ["# Relatório de Satisfação (NPS)\n", f"Gerado em: {datetime.datetime.now().isoformat()}\n\n"]
        if nps_file.exists():
            try:
                with open(nps_file, "r", encoding="utf-8") as f:
                    responses = [json.loads(l) for l in f if l.strip()]
                if responses:
                    scores = [r["score"] for r in responses]
                    report_lines.append(f"Total de respostas: {len(responses)}\n")
                    report_lines.append(f"Média geral: {sum(scores)/len(scores):.1f}\n\n")
                    report_lines.append("## Histórico de Respostas\n\n")
                    report_lines.append("| # | Data | Nota | Classificação | Comentário |\n")
                    report_lines.append("|---|------|------|---------------|------------|\n")
                    for i, r in enumerate(responses, 1):
                        ts_r = r.get("timestamp", "")[:10]
                        s = r.get("score", "")
                        c = r.get("classification", "")
                        cm = r.get("comentario", "").replace("\n", " ")
                        report_lines.append(f"| {i} | {ts_r} | {s} | {c} | {cm} |\n")
                else:
                    report_lines.append("Nenhuma resposta registrada.\n")
            except Exception:
                report_lines.append("Erro ao ler dados NPS.\n")
        report_content = "".join(report_lines)
        tmp_dir = Path(tempfile.mkdtemp())
        (tmp_dir / "relatorio_nps.md").write_text(report_content, encoding="utf-8")
        if nps_file.exists():
            shutil.copy(nps_file, tmp_dir / "nps_responses.jsonl")
        op_file = config_dir / "operation_log.jsonl"
        if op_file.exists():
            shutil.copy(op_file, tmp_dir / "operation_log.jsonl")
        session_file = config_dir / "session.json"
        if session_file.exists():
            shutil.copy(session_file, tmp_dir / "session.json")
        shutil.make_archive(str(zip_path), 'zip', tmp_dir)
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return str(zip_path) + ".zip"

    def _exportar_dados_uso_ui(self):
        TUILayout.clear()
        TUILayout.print_header("EXPORTAR DADOS DE USO")
        print("\n  Isso irá gerar um arquivo .zip na Área de Trabalho com:\n")
        print("    • Relatório NPS")
        print("    • Log de operações (telemetria)")
        print("    • Dados da sessão atual\n")
        if input("  Prosseguir? (S/N): ").upper() != 'S':
            return
        zip_path = self._exportar_nps_zip()
        if zip_path:
            self.menu.print_success(f"\n  Arquivo gerado: {zip_path}")
            print("\n  Envie o arquivo para contato@mundoaec.com")
        else:
            self.menu.print_error("  Erro ao gerar arquivo.")
        input("\n  Pressione Enter para continuar...")

    def _open_workspace_folder(self, config):
        import subprocess
        path = str(config.workspace_path)
        try:
            if sys.platform == 'win32':
                os.startfile(path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', path], check=True)
            else:
                subprocess.run(['xdg-open', path], check=True)
            self.menu.print_success(f"Abrindo pasta: {path}")
        except Exception as e:
            self.menu.print_error(f"Erro ao abrir pasta: {format_error_with_suggestion(e)}")
        input("Pressione Enter para continuar...")

    def handle_installation(self):
        from foton_system.modules.shared.infrastructure.services.install_service import InstallService
        TUILayout.clear()
        TUILayout.print_header("INSTALAÇÃO E ATALHOS")
        print(f"\n  {Fore.WHITE}Isso criara atalhos na Area de Trabalho e Menu Iniciar.")
        print(f"  Garante tambem a pasta de configuracao local.")
        try:
            tip = self.menu.tip_service.get_random_tip("GERAL")
            TUILayout.print_tip(tip, "SETUP")
        except Exception:
            pass
        TUILayout.print_footer()
        if input(f"\n{Fore.YELLOW}Deseja prosseguir? (S/N): {Style.RESET_ALL}").upper() == 'S':
            try:
                result = InstallService().install()
                if result == "KILL_SWITCH":
                    print(f"\n  {Fore.CYAN}O programa sera fechado para concluir a instalacao.{Style.RESET_ALL}")
                    print(f"  {Fore.CYAN}  Ele sera reaberto automaticamente em instantes.{Style.RESET_ALL}")
                    print()
                    input("Pressione Enter para sair...")
                    os._exit(0)
                else:
                    self.menu.print_success("Instalação realizada com sucesso!")
            except Exception as e:
                logger = self.menu._get_logger()
                logger.error(f"Erro critico no menu de instalacao: {e}", exc_info=True)
                self.menu.print_error(f"Erro na instalacao: {format_error_with_suggestion(e)}")
            input("Pressione Enter para voltar...")

    def handle_admin_tools(self):
        try:
            from foton_system.scripts.admin_launcher import main_menu
            main_menu()
        except Exception as e:
            self.menu.print_error(f"Erro: {format_error_with_suggestion(e)}")

    def start_pomodoro_ui(self):
        from foton_system.modules.shared.infrastructure.config.config import Config
        config = Config()
        TUILayout.clear()
        TUILayout.print_header("TIMER POMODORO")
        try:
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
                    df = self.menu.client_repo.get_clients_dataframe()
                    mask = df['Alias'].str.lower().str.contains(term.lower(), na=False)
                    res = df[mask]
                    if not res.empty:
                        client_alias = res.iloc[0]['Alias']
                        self.menu.print_success(f"  Vinculo: {client_alias}")
            from foton_system.modules.productivity.pomodoro import PomodoroTimer
            timer = PomodoroTimer(work, short, long, cycles, client_alias)
            timer.run()
        except Exception as e:
            self.menu.print_error(f"Erro no timer: {format_error_with_suggestion(e)}")

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
                tip = self.menu.tip_service.get_random_tip("IA")
                TUILayout.print_tip(tip, "SENTINELA")
            except Exception:
                pass
            TUILayout.print_footer()
            choice = input(f"{Fore.CYAN}>> {Fore.WHITE}Escolha: {Style.RESET_ALL}").strip()
            if choice == '1':
                self.menu.print_warning("  Iniciando Watcher...")
                try:
                    from foton_system.core.watcher.service import WatcherService
                    self.menu._watcher = WatcherService()
                    self.menu._watcher.start()
                    self.menu.print_success("  Watcher ativado!")
                    input("Enter...")
                except Exception as e:
                    self.menu.print_error(f"Erro: {format_error_with_suggestion(e)}")
                    input("Enter...")
            elif choice == '2':
                if hasattr(self.menu, '_watcher') and self.menu._watcher:
                    self.menu._watcher.stop()
                    self.menu.print_success("  Watcher desativado.")
                else:
                    self.menu.print_warning("  Nenhum watcher ativo.")
                input("Enter...")
            elif choice == '3':
                self.menu._index_knowledge_ui()
            elif choice == '4':
                self.menu._query_knowledge_ui()
            elif choice in ('0', 'b', 'B'):
                break
