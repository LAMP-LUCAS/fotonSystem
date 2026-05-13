"""
TUI Form View - Interface Interativa Navegável.
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
            cmd = input(f"\n{Fore.CYAN}>> Ação ou Novo Valor: {Style.RESET_ALL}").strip().lower()
            
            if cmd == '' or cmd == 'n':
                self.session.next()
            elif cmd == 'p':
                self.session.prev()
            elif cmd == 'v':
                self._show_summary()
            elif cmd == 's':
                if input(f"\n{Fore.GREEN}Confirmar e Salvar Arquivo? (S/N): {Style.RESET_ALL}").lower() == 's':
                    return "save"
            elif cmd == 'c':
                if input(f"\n{Fore.RED}Descartar e Sair? (S/N): {Style.RESET_ALL}").lower() == 's':
                    return "cancel"
            else:
                f = self.session.get_current_field()
                if f and not f.is_calculated:
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
            print(f"  Descrição: {f.description}")
            if f.is_calculated:
                print(f"  Fórmula  : {Fore.GREEN}{f.formula}{Style.RESET_ALL}")
            print(f"\n  {Style.BRIGHT}💡 Valor Atual: {Fore.WHITE}{f.current_value if f.current_value else '(vazio)'}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'-'*60}\n  [ENTER/N] Próxima | [P] Anterior | [V] Resumo | [S] Salvar | [C] Cancelar\n{'='*60}{Style.RESET_ALL}")

    def _show_summary(self):
        self._clear()
        print(f"{Fore.CYAN}{'='*60}\n{Style.BRIGHT}📊 RESUMO DAS ALTERAÇÕES\n{'='*60}{Style.RESET_ALL}")
        for f in self.session.fields:
            status = f"{Fore.YELLOW}*" if f.is_dirty else " "
            color = Fore.GREEN if f.is_calculated else Fore.WHITE
            print(f"{status}{color}@{f.name.ljust(20)}{Style.RESET_ALL}: {f.current_value}")
        input(f"\n{Fore.YELLOW}Pressione ENTER para voltar...{Style.RESET_ALL}")
