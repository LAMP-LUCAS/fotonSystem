"""
ModalEngine: Motor da interface modal inspirada em Vim + tmux.
Gerencia modos (NORMAL, INSERT, VISUAL, COMANDO), buffers, splits e comandos.
RULE-TUI-1.1 a 1.6 e RULE-TUI-2.1 a 2.19
"""

from typing import List, Optional, Dict, Any
from foton_system.interfaces.cli.modal.modal_buffer import ModalBuffer
from foton_system.interfaces.cli.modal.modal_status_bar import ModalStatusBar


class ModalMode:
    NORMAL = "NORMAL"
    INSERT = "INSERT"
    VISUAL = "VISUAL"
    COMANDO = "COMANDO"


class ModalEngine:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.modal_enabled: bool = bool(self.config.get("modal_enabled", False))
        self.theme: str = self.config.get("modal_theme", "default")
        self.current_mode: str = ModalMode.NORMAL

        self.buffers: List[ModalBuffer] = []
        self.active_buffer_idx: int = 0
        self.splits: List[ModalBuffer] = []
        self.message: str = ""
        self.cmdline: str = ""
        self._pending_prefix: str = ""

        # Inicializa com buffer padrao
        default_buf = ModalBuffer("Workspace", ["Bem-vindo ao Foton System (Modo Modal)", "Pressione :help para comandos ou i para editar."])
        self.add_buffer(default_buf)

    @property
    def active_buffer(self) -> ModalBuffer:
        if 0 <= self.active_buffer_idx < len(self.buffers):
            return self.buffers[self.active_buffer_idx]
        return self.buffers[0]

    def add_buffer(self, buffer: ModalBuffer) -> None:
        self.buffers.append(buffer)
        self.active_buffer_idx = len(self.buffers) - 1
        if not self.splits:
            self.splits = [buffer]

    def switch_buffer(self, index_or_name: Any) -> bool:
        if isinstance(index_or_name, int):
            if 0 <= index_or_name < len(self.buffers):
                self.active_buffer_idx = index_or_name
                return True
        elif isinstance(index_or_name, str):
            for i, buf in enumerate(self.buffers):
                if buf.name.lower() == index_or_name.lower():
                    self.active_buffer_idx = i
                    return True
        return False

    def set_mode(self, mode: str) -> None:
        if mode in (ModalMode.NORMAL, ModalMode.INSERT, ModalMode.VISUAL, ModalMode.COMANDO):
            self.current_mode = mode
            self._pending_prefix = ""
            if mode != ModalMode.COMANDO:
                self.cmdline = ""

    def render_status_bar(self) -> str:
        buf = self.active_buffer
        return ModalStatusBar.render(
            mode=self.current_mode,
            buffer_name=buf.name,
            line_idx=buf.cursor_line,
            total_lines=buf.line_count,
            message=self.message,
        )

    def handle_key(self, key: str) -> Optional[str]:
        """
        Processa tecla unica ou comando de acordo com o modo ativo.
        Retorna string de status ou None.
        """
        self.message = ""

        if key == "\x1b" or key == "Esc":  # Escape
            self.set_mode(ModalMode.NORMAL)
            return "NORMAL"

        if self.current_mode == ModalMode.NORMAL:
            return self._handle_normal_key(key)
        elif self.current_mode == ModalMode.INSERT:
            return self._handle_insert_key(key)
        elif self.current_mode == ModalMode.VISUAL:
            return self._handle_visual_key(key)
        elif self.current_mode == ModalMode.COMANDO:
            return self._handle_command_key(key)
        return None

    def _handle_normal_key(self, key: str) -> Optional[str]:
        buf = self.active_buffer

        # Prefix handling (gg)
        if self._pending_prefix == "g":
            if key == "g":
                buf.move_to_top()
                self._pending_prefix = ""
                return "TO_TOP"
            self._pending_prefix = ""

        if key == "g":
            self._pending_prefix = "g"
            return None
        elif key == "G":
            buf.move_to_bottom()
            return "TO_BOTTOM"
        elif key in ("j", "Down"):
            buf.move_down()
        elif key in ("k", "Up"):
            buf.move_up()
        elif key in ("h", "Left"):
            buf.move_left()
        elif key in ("l", "Right"):
            buf.move_right()
        elif key == "i":
            self.set_mode(ModalMode.INSERT)
            return "INSERT"
        elif key == "a":
            buf.move_right()
            self.set_mode(ModalMode.INSERT)
            return "INSERT"
        elif key == "v":
            self.set_mode(ModalMode.VISUAL)
            return "VISUAL"
        elif key == ":":
            self.set_mode(ModalMode.COMANDO)
            self.cmdline = ":"
            return "COMANDO"
        elif key == "/":
            self.set_mode(ModalMode.COMANDO)
            self.cmdline = "/"
            return "SEARCH"
        elif key == "n":
            buf.next_match()
        elif key == "N":
            buf.prev_match()
        return None

    def _handle_insert_key(self, key: str) -> Optional[str]:
        buf = self.active_buffer
        if key == "\n" or key == "Enter":
            buf.insert_newline()
        elif len(key) == 1:
            buf.insert_text(key)
        return None

    def _handle_visual_key(self, key: str) -> Optional[str]:
        buf = self.active_buffer
        if key in ("j", "Down"):
            buf.move_down()
        elif key in ("k", "Up"):
            buf.move_up()
        elif key in ("h", "Left"):
            buf.move_left()
        elif key in ("l", "Right"):
            buf.move_right()
        return None

    def _handle_command_key(self, key: str) -> Optional[str]:
        if key == "\n" or key == "Enter":
            result = self.execute_command(self.cmdline)
            self.set_mode(ModalMode.NORMAL)
            return result
        elif key in ("\b", "Backspace"):
            if len(self.cmdline) > 1:
                self.cmdline = self.cmdline[:-1]
            else:
                self.set_mode(ModalMode.NORMAL)
        elif len(key) == 1:
            self.cmdline += key
        return None

    def execute_command(self, cmd: str) -> str:
        """Executa comando da linha de comando (:cmd ou /pattern)."""
        cmd = cmd.strip()
        if not cmd:
            return ""

        if cmd.startswith("/"):
            pattern = cmd[1:].strip()
            count = self.active_buffer.search(pattern)
            self.message = f"{count} matches encontrados para '{pattern}'"
            return f"SEARCH:{count}"

        if cmd.startswith(":"):
            cmd = cmd[1:].strip()

        parts = cmd.split(maxsplit=1)
        action = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if action in ("q", "quit"):
            self.message = "Saindo..."
            return "QUIT"
        elif action in ("w", "write"):
            self.active_buffer.modified = False
            self.message = f"Buffer '{self.active_buffer.name}' salvo."
            return "SAVED"
        elif action in ("b", "buffer"):
            if self.switch_buffer(arg):
                self.message = f"Ativado buffer: {self.active_buffer.name}"
                return f"BUFFER_SWITCH:{self.active_buffer.name}"
            self.message = f"Buffer '{arg}' não encontrado."
            return "BUFFER_NOT_FOUND"
        elif action == "help":
            self.message = "Atalhos: j/k=nav, i=insert, v=visual, :=cmd, /=busca, :w=save, :q=quit"
            return "HELP"

        self.message = f"Comando desconhecido: :{action}"
        return "UNKNOWN_COMMAND"
