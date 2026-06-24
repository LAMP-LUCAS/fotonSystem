"""Tests: validate_service_codes e fix_service_codes (FASE D)."""
import pytest
import pandas as pd
from unittest.mock import MagicMock


class TestValidateServiceCodes:
    """validate_service_codes() deve detectar códigos de serviço inválidos."""

    def test_all_valid(self, fake_client_repository):
        """Todos os códigos válidos não geram issues."""
        repo = fake_client_repository(
            services_df=pd.DataFrame({
                'AliasCliente': ['CLI_A', 'CLI_B'],
                'Alias': ['REFORMA', 'PROJETO'],
                'CodServico': ['CLIAREF01', 'CLIBPRO01'],
            })
        )
        from foton_system.modules.clients.application.use_cases.client_crud import validate_service_codes
        issues = validate_service_codes(repo)

        assert len(issues) == 0

    def test_detects_missing(self, fake_client_repository):
        """Código ausente (NaN) é detectado como missing."""
        repo = fake_client_repository(
            services_df=pd.DataFrame({
                'AliasCliente': ['CLI_A'],
                'Alias': ['REFORMA'],
                'CodServico': [None],
            })
        )
        from foton_system.modules.clients.application.use_cases.client_crud import validate_service_codes
        issues = validate_service_codes(repo)

        assert len(issues) == 1
        assert issues[0]['issue'] == 'missing'
        assert issues[0]['service_alias'] == 'REFORMA'

    def test_detects_placeholder(self, fake_client_repository):
        """Código placeholder '000' é detectado."""
        repo = fake_client_repository(
            services_df=pd.DataFrame({
                'AliasCliente': ['CLI_A'],
                'Alias': ['REFORMA'],
                'CodServico': ['000'],
            })
        )
        from foton_system.modules.clients.application.use_cases.client_crud import validate_service_codes
        issues = validate_service_codes(repo)

        assert len(issues) == 1
        assert issues[0]['issue'] == 'placeholder'

    def test_detects_invalid_format(self, fake_client_repository):
        """Código com caracteres especiais é detectado como invalid_format."""
        repo = fake_client_repository(
            services_df=pd.DataFrame({
                'AliasCliente': ['CLI_A'],
                'Alias': ['REFORMA'],
                'CodServico': ['COD@#$!'],
            })
        )
        from foton_system.modules.clients.application.use_cases.client_crud import validate_service_codes
        issues = validate_service_codes(repo)

        assert len(issues) == 1
        assert issues[0]['issue'] == 'invalid_format'

    def test_detects_duplicate(self, fake_client_repository):
        """Código duplicado é detectado."""
        repo = fake_client_repository(
            services_df=pd.DataFrame({
                'AliasCliente': ['CLI_A', 'CLI_B'],
                'Alias': ['REFORMA', 'PROJETO'],
                'CodServico': ['CLIAREF01', 'CLIAREF01'],
            })
        )
        from foton_system.modules.clients.application.use_cases.client_crud import validate_service_codes
        issues = validate_service_codes(repo)

        duplicates = [i for i in issues if i['issue'] == 'duplicate']
        assert len(duplicates) == 2

    def test_mixed_issues(self, fake_client_repository):
        """Múltiplos tipos de issues são reportados corretamente."""
        repo = fake_client_repository(
            services_df=pd.DataFrame({
                'AliasCliente': ['CLI_A', 'CLI_B', 'CLI_C'],
                'Alias': ['SVC1', 'SVC2', 'SVC3'],
                'CodServico': ['VALID01', '000', None],
            })
        )
        from foton_system.modules.clients.application.use_cases.client_crud import validate_service_codes
        issues = validate_service_codes(repo)

        assert len(issues) == 2
        types = {i['issue'] for i in issues}
        assert 'placeholder' in types
        assert 'missing' in types


class TestFixServiceCodes:
    """fix_service_codes() deve corrigir códigos inválidos."""

    def test_fix_placeholder(self, fake_client_repository):
        """Placeholder '000' é substituído por código único."""
        repo = fake_client_repository(
            services_df=pd.DataFrame({
                'AliasCliente': ['CLI_A'],
                'Alias': ['REFORMA'],
                'CodServico': ['000'],
            })
        )
        from foton_system.modules.clients.application.use_cases.client_crud import validate_service_codes, fix_service_codes

        issues = validate_service_codes(repo)
        fixed = fix_service_codes(repo, issues)

        assert fixed == 1
        sdf = repo.get_services_dataframe()
        assert sdf.at[0, 'CodServico'] != '000'
        assert sdf.at[0, 'CodServico'] == 'CLIREF01'

    def test_fix_multiple(self, fake_client_repository):
        """Múltiplos códigos inválidos são corrigidos."""
        repo = fake_client_repository(
            services_df=pd.DataFrame({
                'AliasCliente': ['CLI_A', 'CLI_A', 'CLI_B'],
                'Alias': ['SVC1', 'SVC2', 'SVC3'],
                'CodServico': ['000', None, 'INVALID!'],
            })
        )
        from foton_system.modules.clients.application.use_cases.client_crud import validate_service_codes, fix_service_codes

        issues = validate_service_codes(repo)
        fixed = fix_service_codes(repo, issues)

        assert fixed >= 2
        sdf = repo.get_services_dataframe()
        codes = sdf['CodServico'].tolist()
        assert all(c is not None and not pd.isna(c) for c in codes)
        assert len(set(codes)) == len(codes)

    def test_fix_duplicates(self, fake_client_repository):
        """Códigos duplicados são resolvidos com códigos únicos."""
        repo = fake_client_repository(
            services_df=pd.DataFrame({
                'AliasCliente': ['CLI_A', 'CLI_B'],
                'Alias': ['REFORMA', 'PROJETO'],
                'CodServico': ['CLIAREF01', 'CLIAREF01'],
            })
        )
        from foton_system.modules.clients.application.use_cases.client_crud import validate_service_codes, fix_service_codes

        issues = validate_service_codes(repo)
        fixed = fix_service_codes(repo, issues)

        assert fixed == 2
        sdf = repo.get_services_dataframe()
        codes = sdf['CodServico'].tolist()
        assert len(set(codes)) == 2
        assert codes[0] != codes[1]
