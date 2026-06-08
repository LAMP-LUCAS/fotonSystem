"""
TUI Layout Helper - Orquestrador de Design e Interface Dinâmica.
Gerencia larguras, quebras de linha, enquadramentos e componentes visuais.
"""

import os
import shutil
import textwrap
import re
from colorama import Fore, Style
from typing import List, Optional

class TUILayout:
    """
    Centraliza as regras de design para a TUI do Foton System.
    Garante que a interface se adapte ao tamanho do terminal e mantenha bordas perfeitas.
    """
    
    DEFAULT_WIDTH = 70
    MIN_WIDTH = 40
    MAX_WIDTH = 100

    @staticmethod
    def get_width() -> int:
        """Calcula a largura ideal baseada no terminal atual."""
        try:
            columns, _ = shutil.get_terminal_size()
            width = min(TUILayout.MAX_WIDTH, max(TUILayout.MIN_WIDTH, columns - 4))
            return width
        except Exception:
            return TUILayout.DEFAULT_WIDTH

    @staticmethod
    def clear():
        """Limpa a tela do terminal usando sequências ANSI (agnóstico)."""
        import sys
        sys.stderr.write('\033[2J\033[H')
        sys.stderr.flush()

    @staticmethod
    def get_visible_len(text: str) -> int:
        """
        Calcula o comprimento visual real de uma string.
        - Ignora sequências de escape ANSI (cores).
        - Compensa Emojis (contam como 2 colunas na maioria dos terminais).
        """
        # 1. Remover cores ANSI
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_text = ansi_escape.sub('', text)
        
        # 2. Heurística para Emojis (maioria ocupa 2 espaços)
        # Regex para range comum de emojis
        emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]', flags=re.UNICODE)
        num_emojis = len(emoji_pattern.findall(clean_text))
        
        return len(clean_text) + num_emojis

    @staticmethod
    def print_line(content: str, width: int, color: str = Fore.CYAN, align: str = 'left'):
        """Desenha uma linha enquadrada com preenchimento resiliente."""
        visible_len = TUILayout.get_visible_len(content)
        padding_needed = max(0, width - visible_len - 4) # 4 = bordas + margens
        
        if align == 'center':
            left_pad = padding_needed // 2
            right_pad = padding_needed - left_pad
            print(f"{color}║ {' ' * left_pad}{content}{' ' * right_pad} {color}║")
        else:
            print(f"{color}║ {content}{' ' * padding_needed} {color}║")

    @staticmethod
    def print_header(title: str, color: str = Fore.CYAN):
        """Desenha um cabeçalho enquadrado."""
        width = TUILayout.get_width()
        print(f"{color}╔{'═' * (width-2)}╗")
        TUILayout.print_line(f"{Style.BRIGHT}{title}{Style.NORMAL}", width, color, align='center')
        print(f"{color}╠{'═' * (width-2)}╣{Style.RESET_ALL}")

    @staticmethod
    def print_footer(color: str = Fore.CYAN):
        """Desenha o fechamento de um box."""
        width = TUILayout.get_width()
        print(f"{color}╚{'═' * (width-2)}╝{Style.RESET_ALL}")

    @staticmethod
    def print_tip(tip: str, context: str = "DICA"):
        """Renderiza uma dica didática com alinhamento de bordas garantido."""
        width = TUILayout.get_width()
        color = Fore.CYAN
        
        # Emojis distorcem o len() do textwrap, então tratamos o prefixo e o wrap separadamente
        emoji_icon = "💡"
        prefix = f" {emoji_icon} {context}: "
        # Visualmente o prefixo ocupa len(prefix) + 1 (por causa do emoji)
        visual_prefix_len = len(prefix) + 1
        
        available_width = width - visual_prefix_len - 5 
        
        wrapper = textwrap.TextWrapper(width=available_width)
        wrapped_lines = wrapper.wrap(tip)
        
        print(f"{color}╠{'─' * (width-2)}╣")
        
        for i, line in enumerate(wrapped_lines):
            if i == 0:
                content = f"{Style.DIM}{Fore.LIGHTBLACK_EX}{prefix}{line}{Style.NORMAL}"
            else:
                content = f"{' ' * visual_prefix_len}{Style.DIM}{Fore.LIGHTBLACK_EX}{line}{Style.NORMAL}"
            
            TUILayout.print_line(content, width, color)

    @staticmethod
    def print_menu_option(key: str, label: str, color: str = Fore.CYAN):
        """Renderiza uma opção de menu alinhada."""
        width = TUILayout.get_width()
        content = f"{Fore.YELLOW}{key}. {Fore.WHITE}{label}"
        TUILayout.print_line(content, width, color)

    @staticmethod
    def print_field(label: str, value: str, tag: str = "", is_calc: bool = False):
        """Renderiza um campo de formulário."""
        tag_color = Fore.GREEN if is_calc else Fore.BLUE
        print(f"\n  {Fore.WHITE}{label}: {Style.BRIGHT}{value}{Style.RESET_ALL} {tag_color}{tag}{Style.RESET_ALL}")

    @staticmethod
    def wrap_text(text: str, indent: int = 4) -> str:
        """Quebra um texto longo para a largura do terminal."""
        width = TUILayout.get_width() - indent - 4
        wrapper = textwrap.TextWrapper(width=width, initial_indent=" " * indent, subsequent_indent=" " * indent)
        return "\n".join(wrapper.wrap(text))
