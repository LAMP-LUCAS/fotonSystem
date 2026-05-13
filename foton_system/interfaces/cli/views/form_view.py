"""
TUI Form View - Interface Interativa.
Renderiza o formato do arquivo no visualizador com destaque para edições.
"""

import os
from colorama import Fore, Style
from foton_system.modules.documents.domain.models.form_session import FormSession

class TUIFormView:
    def __init__(self, session: FormSession, title: str = "Preencher Ficha"):
        self.session = session
        self.title = title

    def _clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

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
        self._clear()
        f = self.session.get_current_field()
        idx, total = self.session.cursor + 1, len(self.session.fields)
        print(f"{Fore.CYAN}{'='*60}\n{Style.BRIGHT}📋 {self.title.upper()}\n{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Progresso: [{idx}/{total}]{Style.RESET_ALL}\n")
        if f:
            tag = f"{Fore.GREEN}[📐 CALC]" if f.is_calculated else f"{Fore.BLUE}[✍️ INPUT]"
            print(f"  Variável : {Style.BRIGHT}@{f.name}{Style.RESET_ALL} {tag}")
            label = "Valor/Desc" if not f.is_calculated else "Descrição"
            print(f"  {label}: {f.description}")
            if f.hint: print(f"  💡 Dica    : {Fore.YELLOW}{f.hint}{Style.RESET_ALL}")
            if f.is_calculated:
                print(f"  Fórmula  : {Fore.GREEN}{f.formula}{Style.RESET_ALL}")
                print(f"\n  {Style.BRIGHT}✨ Resultado: {Fore.WHITE}{f.current_value}{Style.RESET_ALL}")
            else:
                print(f"\n  {Style.BRIGHT}👉 Valor Atual: {Fore.WHITE}{f.current_value if f.current_value else '(vazio)'}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'-'*60}{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}[ENTER/N]{Style.RESET_ALL} Próxima | {Fore.YELLOW}[P]{Style.RESET_ALL} Anterior | {Fore.YELLOW}[V]{Style.RESET_ALL} Visualizar")
        print(f"  {Fore.GREEN}[S]{Style.RESET_ALL} Salvar | {Fore.CYAN}[A]{Style.RESET_ALL} Salvar Como | {Fore.RED}[C]{Style.RESET_ALL} Cancelar\n{'='*60}{Style.RESET_ALL}")

    def _show_preview(self):
        self._clear()
        print(f"{Fore.CYAN}{'='*60}\n{Style.BRIGHT}📄 PRÉ-VISUALIZAÇÃO DO ARQUIVO\n{'='*60}{Style.RESET_ALL}")
        print(f"{Style.DIM}Legenda: {Fore.WHITE}Original {Fore.CYAN}Modificado {Fore.GREEN}Calculado{Style.RESET_ALL}\n")
        
        field_dict = {f.name: f for f in self.session.fields}
        
        for item in self.session.structure:
            if item["type"] == "text":
                print(f"{Style.DIM}{item['content']}{Style.RESET_ALL}")
            else:
                f = field_dict[item["name"]]
                prefix = f"@{f.name};"
                if f.is_calculated:
                    val = f"[calculo: {f.formula}] {f.description}"
                    print(f"{prefix}{Fore.GREEN}{val}{Style.RESET_ALL}")
                elif f.is_dirty:
                    val = f.current_value
                    if f.hint: val += f" {f.hint}"
                    print(f"{prefix}{Fore.CYAN}{val}{Style.RESET_ALL}")
                else:
                    print(f"{prefix}{f.original_value}")
                    
        input(f"\n{Fore.YELLOW}Pressione ENTER para voltar ao formulário...{Style.RESET_ALL}")
