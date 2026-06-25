from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Dict, Any

class ClientRepositoryPort(ABC):
    @abstractmethod
    def get_clients_dataframe(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_services_dataframe(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def save_clients(self, df: pd.DataFrame):
        pass

    @abstractmethod
    def save_services(self, df: pd.DataFrame):
        pass

    @abstractmethod
    def list_client_folders(self) -> set:
        pass

    @abstractmethod
    def list_service_folders(self, client_name: str) -> set:
        pass

    @abstractmethod
    def create_folder(self, path: str):
        pass

    @abstractmethod
    def soft_delete_client(self, alias: str) -> bool:
        pass

    @abstractmethod
    def soft_delete_service(self, client_alias: str, service_alias: str) -> bool:
        pass

    @abstractmethod
    def restore_client(self, alias: str) -> bool:
        pass

    @abstractmethod
    def get_all_clients_dataframe(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def restore_service(self, client_alias: str, service_alias: str) -> bool:
        pass

    @abstractmethod
    def get_all_services_dataframe(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_deleted_clients(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_deleted_services(self) -> List[Dict[str, Any]]:
        pass
