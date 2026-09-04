import csv
from pathlib import Path
from typing import Optional, List, Dict, Any
from foton_system.modules.finance.application.ports.finance_repository_port import FinanceRepositoryPort
from foton_system.modules.shared.infrastructure.config.logger import setup_logger
from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.clients.domain.models import FinanceEntry

logger = setup_logger()

class CSVFinanceRepository(FinanceRepositoryPort):
    def __init__(self, config: Optional[Config] = None):
        self._config = config

    def _get_ledger_path(self, client_path: Path) -> Path:
        if self._config is None:
            return client_path / 'FINANCEIRO.csv'
        adm_folder = self._config.folder_adm
        new_path = client_path / adm_folder / 'FINANCEIRO.csv'
        legacy_path = client_path / 'FINANCEIRO.csv'
        if new_path.exists():
            return new_path
        if legacy_path.exists():
            return legacy_path
        return new_path

    def save_entry(self, client_path: Path, entry: List[str], headers: List[str]) -> None:
        file_path = self._get_ledger_path(client_path)
        is_new = not file_path.exists()
        
        try:
            with open(file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if is_new:
                    writer.writerow(headers)
                writer.writerow(entry)
        except Exception as e:
            logger.error(f"Erro ao salvar entrada financeira em {file_path}: {e}")
            raise

    def get_entries(self, client_path: Path) -> List[FinanceEntry]:
        file_path = self._get_ledger_path(client_path)
        if not file_path.exists():
            return []

        entries = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    entry = FinanceEntry.from_row(row)
                    if entry is not None:
                        entries.append(entry)
        except Exception as e:
            logger.error(f"Erro ao ler entradas financeiras de {file_path}: {e}")
            return []
        
        return entries
