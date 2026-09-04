"""
Barra de status modo-consciente para a TUI Modal.
Exibe modo atual, nome do buffer, linhas e hora.
"""

from datetime import datetime


class ModalStatusBar:
    MODE_COLORS = {
        "NORMAL": "\033[44;37m",   # Azul
        "INSERT": "\033[42;30m",   # Verde
        "VISUAL": "\033[45;37m",   # Magenta
        "COMANDO": "\033[43;30m",  # Amarelo
    }
    RESET = "\033[0m"

    @classmethod
    def render(cls, mode: str, buffer_name: str, line_idx: int, total_lines: int, message: str = "") -> str:
        color = cls.MODE_COLORS.get(mode.upper(), "\033[47;30m")
        hora = datetime.now().strftime("%H:%M:%S")
        pos = f"{line_idx + 1}/{max(1, total_lines)}"

        mode_badge = f"{color} -- {mode.upper()} -- {cls.RESET}"
        buf_info = f" {buffer_name} [{pos}]"
        clock = f"{hora} "

        # Layout simplificado para linha de status
        bar = f"{mode_badge}{buf_info} | {clock}"
        if message:
            bar += f"\n\033[36mℹ {message}\033[0m"
        return bar
