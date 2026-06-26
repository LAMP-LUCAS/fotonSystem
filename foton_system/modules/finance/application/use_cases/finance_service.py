from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from foton_system.modules.shared.infrastructure.utils.formatting import FotonFormatter
from foton_system.modules.finance.application.ports.finance_repository_port import FinanceRepositoryPort
from foton_system.modules.clients.domain.models import FinanceEntry


class FinanceService:
    def __init__(self, repository: FinanceRepositoryPort):
        self.repository = repository
        self.headers = ['Data', 'Descricao', 'Tipo', 'Valor']

    def add_entry(
        self,
        client_path: Path,
        description: str = "",
        value: Any = 0.0,
        entry_type: str = 'ENTRADA',
        entry: Optional[FinanceEntry] = None,
    ) -> Dict[str, float]:
        """
        Adiciona uma movimentacao financeira e retorna o resumo.

        Aceita 2 modos:
        1. Legado (params): add_entry(client_path, description, value, entry_type)
        2. Novo (tipado): add_entry(client_path, entry=FinanceEntry(...))

        Se uma entrada com mesma descricao, valor e data ja existir,
        inclui 'duplicate_warning: True' no retorno (warning nao bloqueante).
        """
        if entry is not None:
            description = entry.descricao
            clean_value = entry.valor
            entry_type = entry.tipo
            today = entry.data or datetime.now().strftime('%Y-%m-%d')
        else:
            if isinstance(value, str):
                clean_value = FotonFormatter.parse_br_number(value)
            else:
                clean_value = float(value)
            today = datetime.now().strftime('%Y-%m-%d')

        entry_row = [
            today,
            description,
            entry_type.upper(),
            f"{clean_value:.2f}"
        ]

        existing_entries = self.repository.get_entries(client_path)
        is_duplicate = any(
            e.descricao == description
            and abs(float(e.valor) - clean_value) < 0.01
            and e.data == today
            for e in existing_entries
        )

        self.repository.save_entry(client_path, entry_row, self.headers)
        summary = self.get_summary(client_path)

        if is_duplicate:
            summary['duplicate_warning'] = True

        return summary

    def get_summary(self, client_path: Path) -> Dict[str, float]:
        """
        Calcula o resumo financeiro a partir das entradas do repositorio.
        """
        entries = self.repository.get_entries(client_path)

        entradas = 0.0
        saidas = 0.0

        for entry in entries:
            try:
                val = float(entry.valor)
                if entry.tipo == 'ENTRADA':
                    entradas += val
                else:
                    saidas += val
            except (ValueError, AttributeError):
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
