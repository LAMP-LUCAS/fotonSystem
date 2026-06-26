from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any

from foton_system.modules.clients.domain.models import FinanceEntry

class FinanceRepositoryPort(ABC):
    @abstractmethod
    def save_entry(self, client_path: Path, entry: List[str], headers: List[str]) -> None:
        """Saves a financial entry to the client's ledger."""
        pass

    @abstractmethod
    def get_entries(self, client_path: Path) -> List[FinanceEntry]:
        """Retrieves all financial entries for a client as List[FinanceEntry]."""
        pass
