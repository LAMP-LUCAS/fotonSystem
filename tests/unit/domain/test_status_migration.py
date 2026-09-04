"""Tests for STORY-010: Domain Model — Status Column Migration.

Covers:
- RULE-DOMAIN-1.4: Status column fallback to "ATIVO"
- RULE-DOMAIN-1.5: _ensure_database_exists() creates Status + CodCliente
- RULE-DOMAIN-1.6: FakeClientRepository supports Status column
"""

import pytest
import pandas as pd
import tempfile
from pathlib import Path


class TestGetClientsDataframeFallback:
    """RULE-DOMAIN-1.4: Status column fallback to 'ATIVO' if absent."""

    def test_get_clients_dataframe_adds_status_when_missing(self, fake_client_repository):
        """When Status column is missing, it should be added with 'ATIVO'."""
        RepoClass = fake_client_repository
        repo = RepoClass(
            clients_df=pd.DataFrame({'Alias': ['CLI01'], 'NomeCliente': ['Teste']})
        )
        df = repo.get_clients_dataframe()
        assert 'Status' in df.columns
        assert (df['Status'] == 'ATIVO').all()

    def test_get_clients_dataframe_preserves_existing_status(self, fake_client_repository):
        """When Status column exists, it should not be overwritten."""
        RepoClass = fake_client_repository
        repo = RepoClass(
            clients_df=pd.DataFrame({
                'Alias': ['CLI01'], 'NomeCliente': ['Teste'], 'Status': ['DELETADO']
            })
        )
        df = repo.get_all_clients_dataframe()
        assert df.loc[0, 'Status'] == 'DELETADO'

    def test_get_services_dataframe_adds_status_when_missing(self, fake_client_repository):
        """When Status column is missing in services, it should be added."""
        RepoClass = fake_client_repository
        repo = RepoClass(
            services_df=pd.DataFrame({'Alias': ['SRV01'], 'AliasCliente': ['CLI01']})
        )
        df = repo.get_services_dataframe()
        assert 'Status' in df.columns
        assert (df['Status'] == 'ATIVO').all()

    def test_get_clients_filters_deleted_by_default(self, fake_client_repository):
        """get_clients_dataframe should filter out DELETADO records."""
        RepoClass = fake_client_repository
        repo = RepoClass(
            clients_df=pd.DataFrame({
                'Alias': ['CLI01', 'CLI02'],
                'NomeCliente': ['Teste', 'Outro'],
                'Status': ['ATIVO', 'DELETADO'],
            })
        )
        df = repo.get_clients_dataframe()
        assert len(df) == 1
        assert df.iloc[0]['Alias'] == 'CLI01'


class TestEnsureDatabaseExists:
    """RULE-DOMAIN-1.5: _ensure_database_exists() creates Status + CodCliente."""

    @pytest.fixture(autouse=True)
    def setup_sandbox(self, tmp_path):
        from foton_system.modules.shared.infrastructure.services.path_manager import (
            PathManager,
        )
        PathManager._sandbox_dir = tmp_path
        PathManager.set_sandbox_mode(True)
        PathManager.ensure_directories()
        yield
        PathManager.set_sandbox_mode(False)

    def test_ensure_database_creates_status_column(self, mock_config):
        """New database should have Status column in both sheets."""
        from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import (
            ExcelClientRepository,
        )

        repo = ExcelClientRepository(config=mock_config)
        repo._ensure_database_exists()

        df_clients = pd.read_excel(mock_config.base_dados, sheet_name='baseClientes')
        df_services = pd.read_excel(mock_config.base_dados, sheet_name='baseServicos')

        assert 'Status' in df_clients.columns
        assert 'Status' in df_services.columns

    def test_ensure_database_creates_codcliente_column(self, mock_config):
        """New database should have CodCliente column in baseClientes."""
        from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import (
            ExcelClientRepository,
        )

        repo = ExcelClientRepository(config=mock_config)
        repo._ensure_database_exists()

        df_clients = pd.read_excel(mock_config.base_dados, sheet_name='baseClientes')
        assert 'CodCliente' in df_clients.columns


class TestFakeClientRepositoryStatus:
    """RULE-DOMAIN-1.6: FakeClientRepository supports Status column."""

    def test_fake_default_columns_include_status(self, fake_client_repository):
        """FakeClientRepository default DataFrame should include Status column."""
        RepoClass = fake_client_repository
        repo = RepoClass()
        df = repo.get_clients_dataframe()
        assert 'Status' in df.columns
        assert df.empty or (df['Status'] == 'ATIVO').all()

    def test_fake_default_services_include_status(self, fake_client_repository):
        """FakeClientRepository default services DataFrame should include Status."""
        RepoClass = fake_client_repository
        repo = RepoClass()
        df = repo.get_services_dataframe()
        assert 'Status' in df.columns

    def test_fake_soft_delete_works_with_default_status(self, fake_client_repository):
        """soft_delete_client should work without manually adding Status column."""
        RepoClass = fake_client_repository
        repo = RepoClass(
            clients_df=pd.DataFrame({
                'Alias': ['CLI01'], 'NomeCliente': ['Teste'], 'Status': ['ATIVO'],
            })
        )
        result = repo.soft_delete_client('CLI01')
        assert result is True
        df = repo.get_all_clients_dataframe()
        assert df.loc[0, 'Status'] == 'DELETADO'

    def test_fake_restore_works_with_default_status(self, fake_client_repository):
        """restore_client should work with Status column present."""
        RepoClass = fake_client_repository
        repo = RepoClass(
            clients_df=pd.DataFrame({
                'Alias': ['CLI01'], 'NomeCliente': ['Teste'], 'Status': ['DELETADO'],
            })
        )
        result = repo.restore_client('CLI01')
        assert result is True
        df = repo.get_all_clients_dataframe()
        assert df.loc[0, 'Status'] == 'ATIVO'

    def test_fake_get_deleted_clients_returns_list(self, fake_client_repository):
        """get_deleted_clients should return records with Status='DELETADO'."""
        RepoClass = fake_client_repository
        repo = RepoClass(
            clients_df=pd.DataFrame({
                'Alias': ['CLI01', 'CLI02'],
                'NomeCliente': ['Ativo', 'Deletado'],
                'Status': ['ATIVO', 'DELETADO'],
            })
        )
        deleted = repo.get_deleted_clients()
        assert len(deleted) == 1
        assert deleted[0]['Alias'] == 'CLI02'
