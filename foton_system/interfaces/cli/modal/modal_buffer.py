"""
Buffer de conteúdo para a interface modal TUI.
Suporta navegação em linhas, busca de padrões e seleção de texto.
"""

from typing import List, Tuple, Optional


class ModalBuffer:
    def __init__(self, name: str = "[Sem Nome]", content: Optional[List[str]] = None):
        self.name = name
        self.lines: List[str] = content if content is not None else [""]
        self.cursor_line: int = 0
        self.cursor_col: int = 0
        self.modified: bool = False
        self.search_matches: List[Tuple[int, int]] = []
        self.active_search_idx: int = -1

    @property
    def line_count(self) -> int:
        return len(self.lines)

    @property
    def current_line_text(self) -> str:
        if 0 <= self.cursor_line < len(self.lines):
            return self.lines[self.cursor_line]
        return ""

    def move_down(self, steps: int = 1) -> None:
        self.cursor_line = min(len(self.lines) - 1, self.cursor_line + steps)
        self._clamp_col()

    def move_up(self, steps: int = 1) -> None:
        self.cursor_line = max(0, self.cursor_line - steps)
        self._clamp_col()

    def move_to_top(self) -> None:
        self.cursor_line = 0
        self.cursor_col = 0

    def move_to_bottom(self) -> None:
        self.cursor_line = max(0, len(self.lines) - 1)
        self._clamp_col()

    def move_left(self, steps: int = 1) -> None:
        self.cursor_col = max(0, self.cursor_col - steps)

    def move_right(self, steps: int = 1) -> None:
        max_col = len(self.current_line_text)
        self.cursor_col = min(max_col, self.cursor_col + steps)

    def _clamp_col(self) -> None:
        line_len = len(self.current_line_text)
        if self.cursor_col > line_len:
            self.cursor_col = max(0, line_len)

    def search(self, pattern: str) -> int:
        """Busca padrão case-insensitive no buffer e armazena matches."""
        self.search_matches = []
        self.active_search_idx = -1
        if not pattern:
            return 0

        lowered = pattern.lower()
        for idx, line in enumerate(self.lines):
            line_low = line.lower()
            start = 0
            while True:
                pos = line_low.find(lowered, start)
                if pos == -1:
                    break
                self.search_matches.append((idx, pos))
                start = pos + len(pattern)

        if self.search_matches:
            self.active_search_idx = 0
            self.cursor_line, self.cursor_col = self.search_matches[0]
        return len(self.search_matches)

    def next_match(self) -> bool:
        if not self.search_matches:
            return False
        self.active_search_idx = (self.active_search_idx + 1) % len(self.search_matches)
        self.cursor_line, self.cursor_col = self.search_matches[self.active_search_idx]
        return True

    def prev_match(self) -> bool:
        if not self.search_matches:
            return False
        self.active_search_idx = (self.active_search_idx - 1) % len(self.search_matches)
        self.cursor_line, self.cursor_col = self.search_matches[self.active_search_idx]
        return True

    def insert_text(self, text: str) -> None:
        """Insere texto na posicao atual do cursor (Modo INSERT)."""
        if not self.lines:
            self.lines = [""]
        line = self.lines[self.cursor_line]
        col = self.cursor_col
        self.lines[self.cursor_line] = line[:col] + text + line[col:]
        self.cursor_col += len(text)
        self.modified = True

    def insert_newline(self) -> None:
        """Insere quebra de linha."""
        line = self.lines[self.cursor_line]
        col = self.cursor_col
        left = line[:col]
        right = line[col:]
        self.lines[self.cursor_line] = left
        self.lines.insert(self.cursor_line + 1, right)
        self.cursor_line += 1
        self.cursor_col = 0
        self.modified = True
