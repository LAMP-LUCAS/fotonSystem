"""Tests: fill_missing_codes preenche CodCliente/CodServico NaN (FASE B)."""
import pytest
import pandas as pd
from unittest.mock import MagicMock


class TestFillMissingCodes:
    """fill_missing_codes() deve gerar códigos para registros com NaN."""

    def test_fill_client_codes(self, fake_client_repository):
        """Clientes com CodCliente NaN recebem código único."""
        repo = fake_client_repository(
            clients_df=pd.DataFrame({
                'NomeCliente': ['João Silva', 'Maria Souza', 'Pedro Santos'],
                'Alias': ['JOAO', 'MARIA', 'PEDRO'],
                'CodCliente': [None, None, 'PED01'],
            })
        )

        from foton_system.modules.clients.application.use_cases.client_crud import fill_missing_codes
        result = fill_missing_codes(repo, MagicMock())

        df = repo.get_clients_dataframe()
        codes = df['CodCliente'].tolist()
        assert result['clientes_alterados'] == 2
        assert pd.isna(codes[2]) is False or codes[2] == 'PED01'
        # Codes must be non-null and unique
        assert all(c is not None and not pd.isna(c) for c in codes)
        assert len(set(codes)) == len(codes), f"Codes must be unique: {codes}"

    def test_fill_service_codes(self, fake_client_repository):
        """Serviços com CodServico NaN recebem código único."""
        repo = fake_client_repository(
            services_df=pd.DataFrame({
                'AliasCliente': ['CLI_A', 'CLI_A', 'CLI_B'],
                'Alias': ['SVC_1', 'SVC_2', 'SVC_3'],
                'CodServico': [None, None, 'CLBSV01'],
            })
        )

        from foton_system.modules.clients.application.use_cases.client_crud import fill_missing_codes
        result = fill_missing_codes(repo, MagicMock())

        df = repo.get_services_dataframe()
        codes = df['CodServico'].tolist()
        assert result['servicos_alterados'] == 2
        assert all(c is not None and not pd.isna(c) for c in codes)
        assert len(set(codes)) == len(codes), f"Codes must be unique: {codes}"

    def test_fill_both_clients_and_services(self, fake_client_repository):
        """Preenche clientes e serviços simultaneamente."""
        repo = fake_client_repository(
            clients_df=pd.DataFrame({
                'NomeCliente': ['Ana'],
                'Alias': ['ANA'],
                'CodCliente': [None],
            }),
            services_df=pd.DataFrame({
                'AliasCliente': ['ANA'],
                'Alias': ['PROJ'],
                'CodServico': [None],
            })
        )

        from foton_system.modules.clients.application.use_cases.client_crud import fill_missing_codes
        result = fill_missing_codes(repo, MagicMock())

        assert result['clientes_alterados'] == 1
        assert result['servicos_alterados'] == 1

        cdf = repo.get_clients_dataframe()
        sdf = repo.get_services_dataframe()
        assert not pd.isna(cdf.at[0, 'CodCliente'])
        assert not pd.isna(sdf.at[0, 'CodServico'])

    def test_no_changes_when_all_codes_present(self, fake_client_repository):
        """Nenhuma alteração se todos os códigos já existem."""
        repo = fake_client_repository(
            clients_df=pd.DataFrame({
                'NomeCliente': ['Ana'],
                'Alias': ['ANA'],
                'CodCliente': ['ANA01'],
            }),
            services_df=pd.DataFrame({
                'AliasCliente': ['ANA'],
                'Alias': ['PROJ'],
                'CodServico': ['ANAPROJ01'],
            })
        )

        from foton_system.modules.clients.application.use_cases.client_crud import fill_missing_codes
        result = fill_missing_codes(repo, MagicMock())

        assert result['clientes_alterados'] == 0
        assert result['servicos_alterados'] == 0

    def test_fill_missing_codes_via_service(self, fake_client_repository):
        """ClientService.fill_missing_codes delega para client_crud."""
        repo = fake_client_repository(
            clients_df=pd.DataFrame({
                'NomeCliente': ['Teste'],
                'Alias': ['TESTE'],
                'CodCliente': [None],
            })
        )

        from foton_system.modules.clients.application.use_cases.client_service import ClientService
        service = ClientService(repo)
        result = service.fill_missing_codes()

        assert result['clientes_alterados'] == 1
        df = repo.get_clients_dataframe()
        assert not pd.isna(df.at[0, 'CodCliente'])
