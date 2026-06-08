"""
TUI Form View - Interface Interativa.
Renderiza o formato do arquivo no visualizador com destaque para edições.
"""

from colorama import Fore, Style
from foton_system.modules.documents.domain.models.form_session import FormSession
from foton_system.modules.shared.infrastructure.services.tip_service import TipService
from foton_system.interfaces.cli.views.tui_layout import TUILayout

class TUIFormView:
    def __init__(self, session: FormSession, title: str = "Preencher Ficha"):
        self.session = session
        self.title = title
        self.tip_service = TipService()

    def run_loop(self) -> str:
        while True:
            self._draw()
            cmd = input(f"\n{Fore.CYAN}>> Ação ou Novo Valor: {Style.RESET_ALL}").strip()
            cmd_lower = cmd.lower()
            if cmd_lower == '' or cmd_lower == 'n': self.session.next()
            elif cmd_lower == 'p': self.session.prev()
            elif cmd_lower == 'v': self._show_preview()
            elif cmd_lower == 's':
                if input(f"\n{Fore.GREEN}Salvar? (S/N): {Style.RESET_ALL}").lower() == 's': return "save"
            elif cmd_lower == 'a':
                return "save_as"
            elif cmd_lower == 'c':
                if input(f"\n{Fore.RED}Sair sem salvar? (S/N): {Style.RESET_ALL}").lower() == 's': return "cancel"
            else:
                f = self.session.get_current_field()
                if f and not f.is_calculated:
                    if cmd:
                        self.session.update_current(cmd)
                        self.session.next()

    def _draw(self):
        TUILayout.clear()
        f = self.session.get_current_field()
        idx, total = self.session.cursor + 1, len(self.session.fields)
        
        TUILayout.print_header(self.title)
        
        print(f"\n  {Fore.YELLOW}Progresso: [{idx}/{total}]{Style.RESET_ALL}")
        
        if f:
            tag = "[📐 CALC]" if f.is_calculated else "[✍️ INPUT]"
            TUILayout.print_field(f"Variável @{f.name}", tag, is_calc=f.is_calculated)
            
            label = "Valor/Desc" if not f.is_calculated else "Descrição"
            print(f"  {Fore.WHITE}{label.ljust(12)}: {f.description}")
            
            if f.hint:
                print(f"  {Fore.YELLOW}Dica{' '*9}: {f.hint}{Style.RESET_ALL}")
            
            if f.is_calculated:
                print(f"  {Fore.GREEN}Fórmula{' '*6}: {f.formula}{Style.RESET_ALL}")
                print(f"\n  {Style.BRIGHT}✨ Resultado: {Fore.WHITE}{f.current_value}{Style.RESET_ALL}")
            else:
                curr = f.current_value if f.current_value else "(vazio)"
                print(f"\n  {Style.BRIGHT}👉 Valor Atual: {Fore.WHITE}{curr}{Style.RESET_ALL}")
        
        # Dica Didática Contextual
        try:
            tip_ctx = "FORMATACAO" if f and not f.is_calculated else "SSOT"
            tip = self.tip_service.get_random_tip(tip_ctx)
            TUILayout.print_tip(tip, "DICA")
        except Exception: pass

        TUILayout.print_footer()
        print(f"  {Fore.YELLOW}[ENTER/N]{Style.RESET_ALL} Próxima | {Fore.YELLOW}[P]{Style.RESET_ALL} Anterior | {Fore.YELLOW}[V]{Style.RESET_ALL} Visualizar")
        print(f"  {Fore.GREEN}[S]{Style.RESET_ALL} Salvar | {Fore.CYAN}[A]{Style.RESET_ALL} Salvar Como | {Fore.RED}[C]{Style.RESET_ALL} Cancelar")

    def _show_preview(self):
        TUILayout.clear()
        TUILayout.print_header("PRÉ-VISUALIZAÇÃO")
        
        print(f"  {Style.DIM}Legenda: {Fore.WHITE}Original {Fore.CYAN}Modificado {Fore.GREEN}Calculado{Style.RESET_ALL}\n")

        field_dict = {f.name: f for f in self.session.fields}

        for item in self.session.structure:
            if item["type"] == "text":
                # Quebra o texto original para não estourar o terminal
                wrapped = TUILayout.wrap_text(item['content'], indent=2)
                print(f"{Style.DIM}{wrapped}{Style.RESET_ALL}")
            else:
                f = field_dict[item["name"]]
                prefix = f"  @{f.name}; "
                if f.is_calculated:
                    val = f"[calculo: {f.formula}] {f.description}"
                    print(f"{prefix}{Fore.GREEN}{val}{Style.RESET_ALL}")
                elif f.is_dirty:
                    val = f.current_value
                    if f.hint: val += f" {f.hint}"
                    print(f"{prefix}{Fore.CYAN}{val}{Style.RESET_ALL}")
                else:
                    print(f"{prefix}{f.original_value}")

        print("")
        TUILayout.print_footer()
        input(f"\n{Fore.YELLOW}Pressione ENTER para voltar ao formulário...{Style.RESET_ALL}")
