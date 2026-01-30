import csv
from pathlib import Path
from datetime import datetime
from foton_system.modules.shared.infrastructure.utils.formatting import FotonFormatter

class FinanceService:
    def __init__(self):
        self.headers = ['Data', 'Descricao', 'Tipo', 'Valor']

    def get_ledger_path(self, client_path):
        return Path(client_path) / 'FINANCEIRO.csv'

    def add_entry(self, client_path, description, value, entry_type='ENTRADA'):
        """
        Adiciona uma movimentação financeira.
        entry_type: 'ENTRADA' ou 'SAIDA'
        """
        file_path = self.get_ledger_path(client_path)
        is_new = not file_path.exists()
        
        # Ensure value is float
        if isinstance(value, str):
            value = FotonFormatter.parse_br_number(value)

        row = [
            datetime.now().strftime('%Y-%m-%d'),
            description,
            entry_type,
            f"{value:.2f}"
        ]

        with open(file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if is_new:
                writer.writerow(self.headers)
            writer.writerow(row)
        
        return self.get_summary(client_path)

    def get_summary(self, client_path):
        file_path = self.get_ledger_path(client_path)
        if not file_path.exists():
            return {'total_entradas': 0.0, 'total_saidas': 0.0, 'saldo': 0.0}

        entradas = 0.0
        saidas = 0.0

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                val = float(row['Valor'])
                if row['Tipo'] == 'ENTRADA':
                    entradas += val
                else:
                    saidas += val
        
        return {
            'total_entradas': entradas,
            'total_saidas': saidas,
            'saldo': entradas - saidas
        }
