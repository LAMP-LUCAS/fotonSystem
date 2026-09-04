"""Tests: create_service_entry persiste serviço no DB com CodServico (FASE D)."""
import pytest
import pandas as pd
from unittest.mock import MagicMock


class TestCreateServiceEntry:
    """create_service_entry() deve criar registro de serviço no DB com código único."""

    def test_create_with_auto_code(self, fake_client_repository):
        """Serviço sem cod_servico recebe código gerado automaticamente."""
        repo = fake_client_repository(
            services_df=pd.DataFrame(columns=['AliasCliente', 'Alias', 'CodServico'])
        )
        from foton_system.modules.clients.application.use_cases.client_crud import create_service_entry
        result = create_service_entry(repo, MagicMock(), 'CLI_A', 'REFORMA')

        assert result['AliasCliente'] == 'CLI_A'
        assert result['Alias'] == 'REFORMA'
        assert result['CodServico'] is not None
        assert len(result['CodServico']) >= 5

        sdf = repo.get_services_dataframe()
        assert len(sdf) == 1
        assert sdf.at[0, 'CodServico'] == result['CodServico']

    def test_create_with_explicit_code(self, fake_client_repository):
        """Serviço com cod_servico explícito usa o código fornecido."""
        repo = fake_client_repository(
            services_df=pd.DataFrame(columns=['AliasCliente', 'Alias', 'CodServico'])
        )
        from foton_system.modules.clients.application.use_cases.client_crud import create_service_entry
        result = create_service_entry(repo, MagicMock(), 'CLI_A', 'PROJ', cod_servico='CUSTOM01')

        assert result['CodServico'] == 'CUSTOM01'
        sdf = repo.get_services_dataframe()
        assert sdf.at[0, 'CodServico'] == 'CUSTOM01'

    def test_raises_on_duplicate(self, fake_client_repository):
        """Criar serviço com alias duplicado deve levantar ValueError."""
        repo = fake_client_repository(
            services_df=pd.DataFrame({
                'AliasCliente': ['CLI_A'],
                'Alias': ['REFORMA'],
                'CodServico': ['CLAREF01'],
            })
        )
        from foton_system.modules.clients.application.use_cases.client_crud import create_service_entry
        with pytest.raises(ValueError, match='já existe'):
            create_service_entry(repo, MagicMock(), 'CLI_A', 'REFORMA')

    def test_raises_on_empty_alias(self, fake_client_repository):
        """Alias vazio deve levantar ValueError."""
        repo = fake_client_repository(
            services_df=pd.DataFrame(columns=['AliasCliente', 'Alias', 'CodServico'])
        )
        from foton_system.modules.clients.application.use_cases.client_crud import create_service_entry
        with pytest.raises(ValueError):
            create_service_entry(repo, MagicMock(), '', 'SVC')
        with pytest.raises(ValueError):
            create_service_entry(repo, MagicMock(), 'CLI', '')

    def test_via_service_wrapper(self, fake_client_repository):
        """ClientService.create_service_entry delega corretamente."""
        repo = fake_client_repository(
            services_df=pd.DataFrame(columns=['AliasCliente', 'Alias', 'CodServico'])
        )
        from foton_system.modules.clients.application.use_cases.client_service import ClientService
        service = ClientService(repo, MagicMock())
        result = service.create_service_entry('CLI_B', 'PROJETO')

        assert result['Alias'] == 'PROJETO'
        assert result['CodServico'] is not None
        sdf = repo.get_services_dataframe()
        assert len(sdf) == 1

    def test_anti_collision(self, fake_client_repository):
        """Código gerado não colide com códigos existentes."""
        repo = fake_client_repository(
            services_df=pd.DataFrame({
                'AliasCliente': ['CLI_A'],
                'Alias': ['SVC_1'],
                'CodServico': ['CLISVC01'],
            })
        )
        from foton_system.modules.clients.application.use_cases.client_crud import create_service_entry
        result = create_service_entry(repo, MagicMock(), 'CLI_A', 'SVC_2')

        assert result['CodServico'] != 'CLISVC01'
        # Same base prefix, should be 02
        assert result['CodServico'] == 'CLISVC02'
