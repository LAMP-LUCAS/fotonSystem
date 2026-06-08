from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.shared.infrastructure.config.logger import setup_logger
from foton_system.modules.clients.application.ports.client_repository_port import ClientRepositoryPort
from foton_system.modules.clients.application.use_cases import client_validation, client_query, client_crud

logger = setup_logger()


@dataclass
class CreatedClient:
    codigo: str
    caminho: Path
    dados: dict


class ClientService:
    def __init__(self, repository: ClientRepositoryPort, config: Optional[Config] = None):
        self.repository = repository
        self._config = config or Config()

    @staticmethod
    def normalize_client_name(name: Optional[str]) -> str:
        return client_validation.normalize_client_name(name)

    def list_service_nodes(self, client_name: str) -> list[dict]:
        ignored = set(self._config.ignored_folders)
        return client_query.list_service_nodes(
            client_name, self._config.base_pasta_clientes, ignored
        )

    def _get_template_sections(self):
        return client_crud.get_template_sections(self._config)

    def resolve_client_path(self, client_name: str) -> Path:
        ignored = set(self._config.ignored_folders + ['.obsidian'])
        return client_query.resolve_client_path(
            client_name, self._config.base_pasta_clientes, ignored
        )

    def generate_client_code(self, name):
        try:
            db_clients = self.repository.get_clients_dataframe()
            existing_codes = set(db_clients['CodCliente'].dropna().values)
        except Exception:
            existing_codes = set()
        return client_query.generate_client_code(name, existing_codes)

    def create_client(self, name: str, tax_id: str = "",
                      email: str = "", phone: str = "", alias: str = "") -> CreatedClient:
        return client_crud.create_client(
            name, self.repository, self._config,
            tax_id=tax_id, email=email, phone=phone, alias=alias
        )

    def list_clients(self) -> list:
        ignored = set(self._config.ignored_folders + ['.obsidian'])
        return client_query.list_clients(self._config.base_pasta_clientes, ignored)

    def read_client_info(self, client_name: str) -> dict:
        client_path = self.resolve_client_path(client_name)
        return client_crud.read_client_info_file(client_path)

    def update_client_info(self, client_name: str, section: str, content: str) -> str:
        client_path = self.resolve_client_path(client_name)
        return client_crud.update_client_info_file(client_path, section, content)

    def sync_clients_db_from_folders(self):
        client_crud.sync_clients_db_from_folders(self.repository)

    def sync_client_folders_from_db(self):
        client_crud.sync_client_folders_from_db(self.repository, self._config)

    def sync_services_db_from_folders(self):
        client_crud.sync_services_db_from_folders(self.repository, self._config)

    def sync_service_folders_from_db(self, client_alias=None):
        client_crud.sync_service_folders_from_db(self.repository, self._config, client_alias=client_alias)

    def export_client_data(self):
        client_crud.export_client_data(self.repository, self._config)

    def export_service_data(self):
        client_crud.export_service_data(self.repository, self._config)

    def import_service_data(self):
        client_crud.import_service_data(self.repository, self._config)

