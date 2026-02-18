import os
import random
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService

class MonkeyDataGenerator:
    """
    Seeds the FOTON System with realistic mock data ("Monkey Data") for testing/demo.
    Creates: Clients, Folder Structures, Markdown Context, and Financial CSVs.
    """
    
    def __init__(self):
        BootstrapService.initialize() # Ensure configs exist
        self.config = Config()
        self.base_path = self.config.base_pasta_clientes
        
        self.client_names = [
            ("Residencia_Silva", "José Silva", "123456789"),
            ("Edificio_Horizonte", "Construtora Horizonte", "987654321"),
            ("Reforma_Escritorio_Adv", "Almeida Advogados", "456789123"),
            ("Loja_Shopping_Sul", "Varejo Sul Ltda", "789123456")
        ]
        
        self.services = [
            "Projeto Arquitetônico", "Consultoria Interiores", 
            "Levantamento Cadastral", "Projeto Executivo", "RRT"
        ]

    def generate(self):
        print(f"🐒 Generating Monkey Data in: {self.base_path}")
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        clients_data = []
        
        for folder_name, full_name, nif in self.client_names:
            # 1. Create Folder
            # Add fake ID prefix typically used
            client_id = random.randint(100, 999)
            folder_nav = f"{client_id}_{folder_name}"
            client_path = self.base_path / folder_nav
            client_path.mkdir(exist_ok=True)
            
            # Subfolders
            (client_path / "01_ADMINISTRATIVO").mkdir(exist_ok=True)
            (client_path / "02_FINANCEIRO").mkdir(exist_ok=True)
            (client_path / "03_PROJETOS").mkdir(exist_ok=True)
            
            print(f"   Ref: {folder_nav}")
            
            # 2. PROJETO_CONTEXTO.md (For RAG)
            self._create_context_file(client_path, full_name, folder_name)
            
            # 3. FINANCEIRO.csv
            balance = self._create_finance_csv(client_path)
            
            # 4. Data for Master Excel
            clients_data.append({
                "Codigo": client_id,
                "Nome": full_name,
                "Apelido": folder_name,
                "NIF": nif,
                "Email": f"contato@{folder_name.lower()}.com",
                "Telefone": f"11 9{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                "Caminho": str(client_path),
                "Saldo": balance
            })
            
        # 5. Update Master Excel (Mock)
        # In a real scenario we might append, here we overwrite for a clean test state if doesnt exist
        # or append if exists.
        # For simplicity of the "reset", let's create a new mock excel if one doesn't exist
        # or just leave it to the user to execute the sync Op later.
        
        print(f"✅ Monkey Data Generation Complete.")
        print(f"Run 'op_index_knowledge' to feed this to the AI.")

    def _create_context_file(self, path: Path, name: str, project_type: str):
        """Creates a rich markdown file for RAG testing."""
        content = f"""# Ficha do Cliente: {name}
Data: {datetime.now().strftime('%Y-%m-%d')}
Tipo: {project_type}

## Contexto do Projeto
O cliente {name} buscou o escritório para desenvolver um projeto de {"Alto Padrão" if "Residencia" in project_type else "Comercial"}.
A principal demanda é a otimização de espaço e uso de materiais sustentáveis.

## Decisões Técnicas
- **Estrutura:** Concreto aparente foi escolhido para a fachada.
- **Acabamentos:** Piso Portinari {random.randint(2023,2025)} para áreas molhadas.
- **Cronograma:** Previsão de entrega para {random.choice(['Dezembro', 'Julho', 'Março'])} de 2026.

## Notas de Reunião
- Cliente prefere tons neutros.
- Orçamento estipulado teto de R$ {random.randint(50, 500)} mil.
- Evitar uso de madeira natural na área externa devido à manutenção.
"""
        with open(path / "INFO-CLIENTE.md", "w", encoding="utf-8") as f:
            f.write(content)

    def _create_finance_csv(self, path: Path) -> float:
        """Creates realistic transaction history."""
        records = []
        saldo = 0.0
        
        # Start date: 3 months ago
        curr_date = datetime.now() - timedelta(days=90)
        
        # Initial Installment
        val = random.randint(2000, 10000)
        records.append([curr_date.strftime('%Y-%m-%d'), "Entrada Projeto", val, "ENTRADA"])
        saldo += val
        
        # Random expenses/income
        for _ in range(random.randint(3, 8)):
            curr_date += timedelta(days=random.randint(5, 15))
            if random.random() > 0.7:
                # Income
                val = random.randint(1000, 5000)
                desc = f"Parcela {random.randint(2,5)}"
                tipo = "ENTRADA"
                saldo += val
            else:
                # Expense
                val = random.randint(50, 500)
                desc = random.choice(["Plotagem", "Uber Visita", "Taxa RRT", "Impressão Croquis"])
                tipo = "SAIDA"
                saldo -= val
            
            records.append([curr_date.strftime('%Y-%m-%d'), desc, val, tipo])
            
        df = pd.DataFrame(records, columns=["Data", "Descricao", "Valor", "Tipo"])
        df.to_csv(path / "FINANCEIRO.csv", index=False)
        
        return saldo

if __name__ == "__main__":
    MonkeyDataGenerator().generate()
