from abc import ABC, abstractmethod
import pandas as pd

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
