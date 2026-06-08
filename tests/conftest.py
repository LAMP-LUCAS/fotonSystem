"""
Shared test configuration and fixtures for Foton System tests.

Provides:
- Path bootstrap (so tests can be run from any directory)
- Common fixtures: FakeClientRepository, reset_factory, mock_config
"""

import sys
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture
def fake_client_repository():
    """In-memory ClientRepositoryPort implementation for fast unit tests.
    
    Implements the same port as ExcelClientRepository but without I/O.
    """
    from foton_system.modules.clients.application.ports.client_repository_port import (
        ClientRepositoryPort,
    )

    class FakeClientRepository(ClientRepositoryPort):
        def __init__(self, clients_df=None, services_df=None, folders=None, service_folders=None):
            self._clients = clients_df if clients_df is not None else pd.DataFrame(
                columns=['Alias', 'NomeCliente', 'CodCliente', 'NIF', 'Email', 'Telefone']
            )
            self._services = services_df if services_df is not None else pd.DataFrame(
                columns=['AliasCliente', 'Alias', 'CodServico']
            )
            self._folders = folders if folders is not None else set()
            self._service_folders = service_folders if service_folders is not None else {}
            self._created_folders = []

        def get_clients_dataframe(self) -> pd.DataFrame:
            return self._clients.copy()

        def get_services_dataframe(self) -> pd.DataFrame:
            return self._services.copy()

        def save_clients(self, df: pd.DataFrame):
            self._clients = df.copy()

        def save_services(self, df: pd.DataFrame):
            self._services = df.copy()

        def list_client_folders(self) -> set:
            return self._folders.copy()

        def list_service_folders(self, client_name: str) -> set:
            return self._service_folders.get(client_name, set()).copy()

        def create_folder(self, path):
            self._created_folders.append(Path(path))

    return FakeClientRepository


@pytest.fixture(autouse=True)
def reset_singletons(request):
    """Reset MCPServiceFactory + Config singletons before/after each test.

    Autouse=True because both singletons are global state that pollutes
    across tests in unpredictable ways. Tests that need different behavior
    can override this fixture locally.

    Why: the patched `Config()` returns the cached real instance if
    `Config._instance` is already set. The other tests (e.g. ones that
    construct `ClientService()` without a `config` argument) pre-populate
    the singleton, which then leaks across tests.
    """
    from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory
    from foton_system.modules.shared.infrastructure.config.config import Config
    MCPServiceFactory.reset()
    Config._instance = None
    yield
    MCPServiceFactory.reset()
    Config._instance = None


@pytest.fixture
def temp_clients_dir(tmp_path):
    """Create a temporary clients directory with sample client folders."""
    (tmp_path / "CLIENT_A").mkdir()
    (tmp_path / "CLIENT_A" / "SERVICE_1").mkdir()
    (tmp_path / "CLIENT_A" / "SERVICE_1" / "doc.pdf").touch()
    (tmp_path / "CLIENT_B").mkdir()
    (tmp_path / "CLIENT_B" / "INFO-CLIENTE.md").write_text(
        "@nomeCliente: CLIENT B\n@cpf: 123.456.789-00\n",
        encoding="utf-8",
    )
    (tmp_path / ".obsidian").mkdir()
    (tmp_path / "DOC").mkdir()
    return tmp_path


@pytest.fixture
def mock_config(temp_clients_dir):
    """Patch Config and inject it explicitly into MCPServiceFactory.

    Why explicit injection: the real ``Config.__new__`` uses
    ``super(Config, cls).__new__(cls)`` with an explicit class reference.
    When the class is patched, ``super(MagicMock, ...)`` raises TypeError.
    We avoid this by:
    1. Creating a ``MagicMock`` that mimics the Config's attributes.
    2. Resetting ``MCPServiceFactory`` and re-instantiating with the mock
       config passed explicitly.
    """
    from unittest.mock import MagicMock
    from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory

    mock_cfg = MagicMock()
    mock_cfg.base_pasta_clientes = temp_clients_dir
    mock_cfg.templates_path = REPO_ROOT / "tests" / "fixtures" / "fake_templates"
    mock_cfg.ignored_folders = ["DOC", "ARQ", "HID", "ELE", "STR", "PL", "EVT"]
    mock_cfg.base_dados = temp_clients_dir / "baseDados.xlsx"

    # Reset and pre-create the factory with the mock config injected
    MCPServiceFactory.reset()
    MCPServiceFactory._instance = MCPServiceFactory(config=mock_cfg)
    yield mock_cfg
    MCPServiceFactory.reset()
