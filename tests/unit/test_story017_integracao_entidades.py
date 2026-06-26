import unittest
import pandas as pd
from pathlib import Path
from typing import List

from foton_system.modules.clients.domain.models import Client, Service, FinanceEntry
from foton_system.modules.clients.application.ports.client_repository_port import ClientRepositoryPort
from foton_system.modules.finance.application.ports.finance_repository_port import FinanceRepositoryPort
from foton_system.modules.finance.application.use_cases.finance_service import FinanceService


class TestExcelClientRepositorioMetodosTipados(unittest.TestCase):
    """Testa que ExcelClientRepository expoe metodos que retornam List[Client] e List[Service]."""

    def test_get_clients_retorna_lista_de_client(self):
        """get_clients() retorna List[Client] com dados do DataFrame."""
        from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import (
            ExcelClientRepository,
        )
        repo = ExcelClientRepository()
        clients = repo.get_clients()
        self.assertIsInstance(clients, list)
        if clients:
            self.assertIsInstance(clients[0], Client)
            self.assertTrue(all(isinstance(c, Client) for c in clients))

    def test_get_clients_filtra_deletado(self):
        """get_clients() nao inclui registros com Status DELETADO."""
        from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import (
            ExcelClientRepository,
        )
        repo = ExcelClientRepository()
        clients = repo.get_clients()
        for c in clients:
            self.assertEqual(c.status, "ATIVO")

    def test_get_services_retorna_lista_de_service(self):
        """get_services() retorna List[Service] com dados do DataFrame."""
        from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import (
            ExcelClientRepository,
        )
        repo = ExcelClientRepository()
        services = repo.get_services()
        self.assertIsInstance(services, list)
        if services:
            self.assertIsInstance(services[0], Service)
            self.assertTrue(all(isinstance(s, Service) for s in services))

    def test_get_services_filtra_deletado(self):
        """get_services() nao inclui registros com Status DELETADO."""
        from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import (
            ExcelClientRepository,
        )
        repo = ExcelClientRepository()
        services = repo.get_services()
        for s in services:
            self.assertEqual(s.status, "ATIVO")

    def test_get_all_clients_retorna_lista_com_deletados(self):
        """get_all_clients() retorna todos os clients, inclusive DELETADO."""
        from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import (
            ExcelClientRepository,
        )
        repo = ExcelClientRepository()
        clients = repo.get_all_clients()
        self.assertIsInstance(clients, list)
        statuses = {c.status for c in clients}
        self.assertIn("ATIVO", statuses)

    def test_get_all_services_retorna_lista_com_deletados(self):
        """get_all_services() retorna todos os services, inclusive DELETADO."""
        from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import (
            ExcelClientRepository,
        )
        repo = ExcelClientRepository()
        services = repo.get_all_services()
        self.assertIsInstance(services, list)


class TestCSVFinanceRepositorioGetEntries(unittest.TestCase):
    """Testa que CSVFinanceRepository.get_entries() retorna List[FinanceEntry]."""

    def setUp(self):
        self.repo_path = Path(__file__).parent.parent / "fixtures" / "fake_clientes"

    def test_get_entries_retorna_lista_de_finance_entry(self):
        """get_entries() retorna List[FinanceEntry]."""
        from foton_system.modules.finance.infrastructure.repositories.csv_finance_repository import (
            CSVFinanceRepository,
        )
        if not self.repo_path.exists():
            self.skipTest("Fixtures nao disponiveis")
        repo = CSVFinanceRepository()
        entries = repo.get_entries(self.repo_path)
        self.assertIsInstance(entries, list)
        if entries:
            self.assertIsInstance(entries[0], FinanceEntry)
            self.assertTrue(all(isinstance(e, FinanceEntry) for e in entries))


class TestFakeClientRepositorioTipado(unittest.TestCase):
    """Testa que FakeClientRepository implementa metodos tipados."""

    def _make_fake_repo(self):
        from foton_system.modules.clients.application.ports.client_repository_port import (
            ClientRepositoryPort,
        )
        import pandas as pd

        class FakeClientRepo(ClientRepositoryPort):
            def __init__(self):
                self._clients = pd.DataFrame(
                    columns=['Alias', 'NomeCliente', 'CodCliente', 'Status']
                )
                self._services = pd.DataFrame(
                    columns=['AliasCliente', 'Alias', 'CodServico', 'Status']
                )
                self._folders = set()
                self._service_folders = {}
                self._created_folders = []

            def get_clients_dataframe(self): return self._clients.copy()
            def get_all_clients_dataframe(self): return self._clients.copy()
            def get_services_dataframe(self): return self._services.copy()
            def get_all_services_dataframe(self): return self._services.copy()
            def save_clients(self, df): self._clients = df.copy()
            def save_services(self, df): self._services = df.copy()
            def list_client_folders(self): return self._folders.copy()
            def list_service_folders(self, client_name): return self._service_folders.get(client_name, set()).copy()
            def create_folder(self, path): self._created_folders.append(path)
            def soft_delete_client(self, alias): return True
            def soft_delete_service(self, ca, sa): return True
            def restore_client(self, alias): return True
            def restore_service(self, ca, sa): return True
            def get_deleted_clients(self): return []
            def get_deleted_services(self): return []

            def get_clients(self):
                from foton_system.modules.clients.domain.models import Client
                df = self.get_clients_dataframe()
                return [Client.from_row(row.to_dict()) for _, row in df.iterrows()]

            def get_services(self):
                from foton_system.modules.clients.domain.models import Service
                df = self.get_services_dataframe()
                return [Service.from_row(row.to_dict()) for _, row in df.iterrows()]

            def get_all_clients(self):
                from foton_system.modules.clients.domain.models import Client
                df = self.get_all_clients_dataframe()
                return [Client.from_row(row.to_dict()) for _, row in df.iterrows()]

            def get_all_services(self):
                from foton_system.modules.clients.domain.models import Service
                df = self.get_all_services_dataframe()
                return [Service.from_row(row.to_dict()) for _, row in df.iterrows()]

        return FakeClientRepo()

    def test_fake_get_clients_retorna_lista_de_client(self):
        """FakeClientRepository.get_clients() retorna List[Client]."""
        repo = self._make_fake_repo()
        clients = repo.get_clients()
        self.assertIsInstance(clients, list)

    def test_fake_get_services_retorna_lista_de_service(self):
        """FakeClientRepository.get_services() retorna List[Service]."""
        repo = self._make_fake_repo()
        services = repo.get_services()
        self.assertIsInstance(services, list)


class TestCreateClientUsaClientEntity:
    """Testa que client_crud.create_client() usa Client entity internamente."""

    def test_create_client_retorna_client(self, mock_config, fake_client_repository):
        """create_client() retorna um objeto Client."""
        from foton_system.modules.clients.application.use_cases.client_crud import create_client
        RepoClass = fake_client_repository
        repo = RepoClass()
        client = create_client("Cliente Teste", repo, mock_config)
        self.assertIsInstance(client, Client)

    @staticmethod
    def assertIsInstance(obj, cls):
        assert isinstance(obj, cls), f"Expected {cls}, got {type(obj)}"

    def test_create_client_persiste_com_to_row(self, mock_config, fake_client_repository):
        """create_client() persiste dados via to_row()."""
        from foton_system.modules.clients.application.use_cases.client_crud import create_client
        RepoClass = fake_client_repository
        repo = RepoClass()
        client = create_client("Outro Cliente", repo, mock_config)
        df = repo.get_clients_dataframe()
        assert client.nome in df['NomeCliente'].values


class TestFinanceServiceRecebeFinanceEntry(unittest.TestCase):
    """Testa que FinanceService.add_entry() recebe FinanceEntry entity."""

    def test_add_entry_aceita_finance_entry(self):
        """add_entry() aceita FinanceEntry como primeiro argumento."""
        import tempfile
        from foton_system.modules.finance.infrastructure.repositories.csv_finance_repository import (
            CSVFinanceRepository,
        )

        temp_dir = Path(tempfile.mkdtemp())
        try:
            repo = CSVFinanceRepository()
            service = FinanceService(repo)

            entry = FinanceEntry(
                tipo="ENTRADA",
                valor=500.0,
                descricao="Pagamento teste",
                data="2026-06-26",
                cliente_alias="CLIENTE_TESTE",
            )

            summary = service.add_entry(temp_dir, entry=entry)
            self.assertIn("saldo", summary)
            self.assertEqual(summary["saldo"], 500.0)
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestToRowFromRowBridge(unittest.TestCase):
    """Testa que to_row() e from_row() sao usados como ponte repositorio <-> dominio."""

    def test_client_from_row_to_row_roundtrip(self):
        """Client.from_row() e to_row() mantem dados consistentes."""
        row = {
            "ID": 1,
            "NomeCliente": "João Silva",
            "Alias": "JOASILVA",
            "CodCliente": "JOS01",
            "Email": "joao@example.com",
            "Telefone": "11999998888",
            "Endereco": "Rua 1",
            "Status": "ATIVO",
        }
        client = Client.from_row(row)
        row_back = client.to_row()
        for key in ("NomeCliente", "Alias", "CodCliente", "Email", "Telefone", "Status"):
            self.assertEqual(row[key], row_back[key])

    def test_service_from_row_to_row_roundtrip(self):
        """Service.from_row() e to_row() mantem dados consistentes."""
        row = {
            "ID": 1,
            "AliasCliente": "JOA",
            "Alias": "RESIDENCIAL",
            "CodServico": "JOARES01",
            "Modalidade": "Projeto Executivo",
            "Status": "ATIVO",
        }
        service = Service.from_row(row)
        row_back = service.to_row()
        for key in ("AliasCliente", "Alias", "CodServico", "Modalidade", "Status"):
            self.assertEqual(row[key], row_back[key])

    def test_finance_entry_from_row_to_row_roundtrip(self):
        """FinanceEntry.from_row() e to_row() mantem dados consistentes."""
        row = {
            "ID": 1,
            "Tipo": "ENTRADA",
            "Valor": 1000.0,
            "Descricao": "Honorarios",
            "Data": "2026-06-01",
            "Cliente": "CLIENTE_X",
        }
        entry = FinanceEntry.from_row(row)
        row_back = entry.to_row()
        self.assertEqual(row["Tipo"], row_back["Tipo"])
        self.assertEqual(row["Valor"], row_back["Valor"])
        self.assertEqual(row["Descricao"], row_back["Descricao"])
        self.assertEqual(row["Cliente"], row_back["Cliente"])


class TestBackwardCompatDataFrame(unittest.TestCase):
    """Testa que metodos legados de DataFrame continuam funcionando."""

    def test_get_clients_dataframe_ainda_funciona(self):
        """get_clients_dataframe() continua retornando pd.DataFrame."""
        from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import (
            ExcelClientRepository,
        )
        repo = ExcelClientRepository()
        df = repo.get_clients_dataframe()
        self.assertIsInstance(df, pd.DataFrame)

    def test_get_services_dataframe_ainda_funciona(self):
        """get_services_dataframe() continua retornando pd.DataFrame."""
        from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import (
            ExcelClientRepository,
        )
        repo = ExcelClientRepository()
        df = repo.get_services_dataframe()
        self.assertIsInstance(df, pd.DataFrame)


if __name__ == "__main__":
    unittest.main()
