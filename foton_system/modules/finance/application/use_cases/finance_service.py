from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from foton_system.modules.shared.infrastructure.utils.formatting import FotonFormatter
from foton_system.modules.finance.application.ports.finance_repository_port import FinanceRepositoryPort

class FinanceService:
    def __init__(self, repository: FinanceRepositoryPort):
        self.repository = repository
        self.headers = ['Data', 'Descricao', 'Tipo', 'Valor']

    def add_entry(self, client_path: Path, description: str, value: Any, entry_type: str = 'ENTRADA') -> Dict[str, float]:
        """
        Adiciona uma movimentação financeira e retorna o resumo.
        """
        # Garantir que o valor seja float (converte se necessário usando o formatador do sistema)
        if isinstance(value, str):
            clean_value = FotonFormatter.parse_br_number(value)
        else:
            clean_value = float(value)

        entry = [
            datetime.now().strftime('%Y-%m-%d'),
            description,
            entry_type,
            f"{clean_value:.2f}"
        ]

        self.repository.save_entry(client_path, entry, self.headers)
        
        return self.get_summary(client_path)

    def get_summary(self, client_path: Path) -> Dict[str, float]:
        """
        Calcula o resumo financeiro a partir das entradas do repositório.
        """
        entries = self.repository.get_entries(client_path)
        
        entradas = 0.0
        saidas = 0.0

        for row in entries:
            try:
                val = float(row['Valor'])
                if row['Tipo'] == 'ENTRADA':
                    entradas += val
                else:
                    saidas += val
            except (ValueError, KeyError):
                continue
        
        return {
            'total_entradas': entradas,
            'total_saidas': saidas,
            'saldo': entradas - saidas
        }
