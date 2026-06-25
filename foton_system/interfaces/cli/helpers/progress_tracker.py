import time


class ProgressTracker:
    def __init__(self, total: int, description: str = "Processando"):
        self.total = total
        self.description = description
        self.current = 0
        self._start_time = time.time()

    def advance(self, item: str = ""):
        self.current = min(self.current + 1, self.total)
        item_label = f" {item}" if item else ""
        print(f"[{self.current}/{self.total}] {self.description}{item_label}...")

    def finish(self):
        elapsed = time.time() - self._start_time
        print(f"[{self.total}/{self.total}] {self.description} concluido em {elapsed:.1f}s")
