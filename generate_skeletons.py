import pandas as pd
import os

# Define paths
base_path = "foton_system/resources/skeleton"
os.makedirs(base_path, exist_ok=True)

# 1. baseClientes.xlsx
# Columns from DataModel.md
client_columns = [
    "Nome", "CPF_CNPJ", "Endereco", "Telefone", "Email", 
    "EstadoCivil", "Profissao", "CidadeProposta", "LocalProposta", "Geolocalizacao"
]
# Create empty DataFrame
df_clients = pd.DataFrame(columns=client_columns)
# Add one example row
df_clients.loc[0] = ["Cliente Exemplo", "000.000.000-00", "Rua Exemplo, 123", "(00) 00000-0000", "email@exemplo.com", "Solteiro", "Arquiteto", "São Paulo", "Rua da Obra, 100", "-23.55, -46.63"]
df_clients.to_excel(f"{base_path}/baseClientes.xlsx", index=False)
print(f"Created {base_path}/baseClientes.xlsx")

# 2. baseServicos.xlsx
# Columns from DataModel.md
service_columns = [
    "CodServico", "Alias", "Modalidade", "Ano", "Demanda", 
    "AreaTotal", "AreaCoberta", "AreaDescoberta", "Detalhes", 
    "Estilo", "Ambientes", "ValorProposta", "ValorContrato"
]
df_services = pd.DataFrame(columns=service_columns)
df_services.loc[0] = ["SRV001", "PROJETO-EXEMPLO", "Residencial", "2024", "Projeto Completo", "100", "80", "20", "Casa de campo", "Moderno", "Sala, Cozinha, 2 Quartos", "10000", "10000"]
df_services.to_excel(f"{base_path}/baseServicos.xlsx", index=False)
print(f"Created {base_path}/baseServicos.xlsx")

# 3. baseDados.xlsx (Central DB - often a combination or just a registry)
# Assuming it links clients and services or acts as a master list. 
# Based on DataModel, it seems to hold similar data. Let's make a generic structure.
# If it's the "System of Record", it might have ID, ClientID, ServiceID, Status, etc.
# For now, I'll create a basic structure that can be expanded.
db_columns = ["ID", "Status", "DataCriacao", "Observacoes"]
df_db = pd.DataFrame(columns=db_columns)
df_db.to_excel(f"{base_path}/baseDados.xlsx", index=False)
print(f"Created {base_path}/baseDados.xlsx")
