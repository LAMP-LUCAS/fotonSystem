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

        Se uma entrada com mesma descrição, valor e data já existir,
        inclui 'duplicate_warning: True' no retorno (warning não bloqueante).
        """
        if isinstance(value, str):
            clean_value = FotonFormatter.parse_br_number(value)
        else:
            clean_value = float(value)

        today = datetime.now().strftime('%Y-%m-%d')
        entry = [
            today,
            description,
            entry_type,
            f"{clean_value:.2f}"
        ]

        existing_entries = self.repository.get_entries(client_path)
        is_duplicate = any(
            e.get('Descricao') == description
            and abs(float(e.get('Valor', 0) or 0) - clean_value) < 0.01
            and e.get('Data') == today
            for e in existing_entries
        )

        self.repository.save_entry(client_path, entry, self.headers)
        summary = self.get_summary(client_path)

        if is_duplicate:
            summary['duplicate_warning'] = True

        return summary

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

    def get_firm_summary(self, client_paths: list) -> list:
        """Aggregate financial summaries across multiple clients.

        Each entry: {name, income, expense, balance}.
        Clients without any financial data are omitted.
        """
        results = []
        for p in client_paths:
            try:
                summary = self.get_summary(p)
            except Exception:
                continue
            if summary.get('total_entradas', 0) == 0 and summary.get('total_saidas', 0) == 0:
                continue
            results.append({
                'name': p.name,
                'income': summary['total_entradas'],
                'expense': summary['total_saidas'],
                'balance': summary['saldo'],
            })
        return results
