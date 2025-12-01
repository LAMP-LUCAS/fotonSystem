import pandas as pd
from pathlib import Path
from datetime import datetime
from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.shared.infrastructure.config.logger import setup_logger
from foton_system.modules.clients.application.ports.client_repository_port import ClientRepositoryPort

logger = setup_logger()
config = Config()

class ExcelClientRepository(ClientRepositoryPort):
    def __init__(self):
        self.base_pasta = config.base_pasta_clientes
        self.base_dados = config.base_dados
        self.base_clientes = config.base_clientes
        self.base_servicos = config.base_servicos

    def check_files(self):
        if not self.base_dados.exists():
            raise FileNotFoundError(f"Base de dados não encontrada: {self.base_dados}")
        if not self.base_pasta.exists():
            raise FileNotFoundError(f"Pasta de clientes não encontrada: {self.base_pasta}")

    def get_clients_dataframe(self) -> pd.DataFrame:
        try:
            return pd.read_excel(self.base_dados, sheet_name='baseClientes')
        except Exception as e:
            logger.error(f"Erro ao ler base de clientes: {e}")
            raise

    def get_services_dataframe(self) -> pd.DataFrame:
        try:
            return pd.read_excel(self.base_dados, sheet_name='baseServicos')
        except Exception as e:
            logger.error(f"Erro ao ler base de serviços: {e}")
            raise

    def list_client_folders(self) -> set:
        return {pasta.name for pasta in self.base_pasta.iterdir() if pasta.is_dir()}

    def list_service_folders(self, client_name: str) -> set:
        client_path = self.base_pasta / client_name
        if client_path.exists() and client_path.is_dir():
            return {pasta.name for pasta in client_path.iterdir() if pasta.is_dir()}
        return set()

    def save_clients(self, df: pd.DataFrame):
        try:
            with pd.ExcelWriter(self.base_dados, mode='a', engine="openpyxl", if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name='baseClientes', index=False)
            
            # Backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.base_dados.parent / f"BKP-baseClientes_{timestamp}.xlsx"
            df.to_excel(backup_path, sheet_name='baseClientes', index=False)
            logger.info(f"Base de clientes salva e backup criado em {backup_path}")
        except Exception as e:
            logger.error(f"Erro ao salvar base de clientes: {e}")
            raise

    def save_services(self, df: pd.DataFrame):
        try:
            with pd.ExcelWriter(self.base_dados, mode='a', engine="openpyxl", if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name='baseServicos', index=False)
            
            # Backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.base_dados.parent / f"BKP-baseServicos_{timestamp}.xlsx"
            df.to_excel(backup_path, sheet_name='baseServicos', index=False)
            logger.info(f"Base de serviços salva e backup criado em {backup_path}")
        except Exception as e:
            logger.error(f"Erro ao salvar base de serviços: {e}")
            raise

    def create_folder(self, path: str):
        path = Path(path)
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Pasta criada: {path}")
        except Exception as e:
            logger.error(f"Erro ao criar pasta {path}: {e}")
            raise
