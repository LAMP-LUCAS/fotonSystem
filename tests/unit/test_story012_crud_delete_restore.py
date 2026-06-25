import pytest
import pandas as pd
from foton_system.core.ops.op_soft_delete_client import OpSoftDeleteClient
from foton_system.core.ops.op_restore_client import OpRestoreClient
from foton_system.core.ops.op_soft_delete_service import OpSoftDeleteService
from foton_system.core.ops.op_restore_service import OpRestoreService
from foton_system.core.ops.op_update_service import OpUpdateService
from foton_system.core.ops.audit_logger import AuditLogger


# @story: STORY-012
# @rule: RULE-DOMAIN-2.1, RULE-DOMAIN-2.2, RULE-DOMAIN-2.3, RULE-DOMAIN-2.4, RULE-DOMAIN-2.7


@pytest.fixture
def repo(fake_client_repository):
    Factory = fake_client_repository
    df_clients = pd.DataFrame({
        'Alias': ['CLIENTE_ATIVO', 'CLIENTE_DELETADO', 'SEM_SERVICO'],
        'NomeCliente': ['Cliente Ativo', 'Cliente Deletado', 'Sem Servico'],
        'CodCliente': ['CLI01', 'CLI02', 'CLI03'],
        'Status': ['ATIVO', 'DELETADO', 'ATIVO'],
    })
    df_services = pd.DataFrame({
        'AliasCliente': ['CLIENTE_ATIVO', 'CLIENTE_ATIVO', 'CLIENTE_DELETADO'],
        'Alias': ['SERVICO_ATIVO', 'SERVICO_DELETADO', 'SERV_ORFAO'],
        'CodServico': ['SRV01', 'SRV02', 'SRV03'],
        'Status': ['ATIVO', 'DELETADO', 'ATIVO'],
        'Modalidade': ['Projeto', 'Projeto', 'Projeto'],
    })
    return Factory(
        clients_df=df_clients,
        services_df=df_services,
    )


# ==============================================================================
# OpSoftDeleteClient — RULE-DOMAIN-2.1
# ==============================================================================

class TestOpSoftDeleteClient:
    def test_soft_delete_active_client(self, repo):
        op = OpSoftDeleteClient(repo, actor="Test")
        result = op.execute(alias="CLIENTE_ATIVO")
        assert result["success"] is True
        assert "CLIENTE_ATIVO" in result["message"]
        df = repo.get_clients_dataframe()
        assert "CLIENTE_ATIVO" not in df['Alias'].values
        all_df = repo.get_all_clients_dataframe()
        assert all_df.loc[all_df['Alias'] == 'CLIENTE_ATIVO', 'Status'].iloc[0] == 'DELETADO'

    def test_soft_delete_already_deleted_raises(self, repo):
        op = OpSoftDeleteClient(repo, actor="Test")
        with pytest.raises(ValueError, match="não encontrado"):
            op.execute(alias="CLIENTE_DELETADO")

    def test_soft_delete_nonexistent_client_raises(self, repo):
        op = OpSoftDeleteClient(repo, actor="Test")
        with pytest.raises(ValueError, match="não encontrado"):
            op.execute(alias="INEXISTENTE")

    def test_soft_delete_empty_alias_raises(self, repo):
        op = OpSoftDeleteClient(repo, actor="Test")
        with pytest.raises(ValueError, match="required"):
            op.execute(alias="")

    def test_soft_delete_audit_attr(self, repo):
        op = OpSoftDeleteClient(repo, actor="TestAudit")
        assert op.audit_logger is not None


# ==============================================================================
# OpRestoreClient — RULE-DOMAIN-2.2
# ==============================================================================

class TestOpRestoreClient:
    def test_restore_deleted_client(self, repo):
        op = OpRestoreClient(repo, actor="Test")
        result = op.execute(alias="CLIENTE_DELETADO")
        assert result["success"] is True
        assert "CLIENTE_DELETADO" in result["message"]
        df = repo.get_clients_dataframe()
        assert "CLIENTE_DELETADO" in df['Alias'].values

    def test_restore_active_client_raises(self, repo):
        op = OpRestoreClient(repo, actor="Test")
        with pytest.raises(ValueError, match="não está deletado"):
            op.execute(alias="CLIENTE_ATIVO")

    def test_restore_nonexistent_client_raises(self, repo):
        op = OpRestoreClient(repo, actor="Test")
        with pytest.raises(ValueError, match="não está deletado"):
            op.execute(alias="INEXISTENTE")

    def test_restore_audit_attr(self, repo):
        op = OpRestoreClient(repo, actor="TestAudit")
        assert op.audit_logger is not None


# ==============================================================================
# OpSoftDeleteService — RULE-DOMAIN-2.3
# ==============================================================================

class TestOpSoftDeleteService:
    def test_soft_delete_active_service(self, repo):
        op = OpSoftDeleteService(repo, actor="Test")
        result = op.execute(client_alias="CLIENTE_ATIVO", service_alias="SERVICO_ATIVO")
        assert result["success"] is True
        assert "SERVICO_ATIVO" in result["message"]
        df = repo.get_services_dataframe()
        assert "SERVICO_ATIVO" not in df['Alias'].values

    def test_soft_delete_already_deleted_service_raises(self, repo):
        op = OpSoftDeleteService(repo, actor="Test")
        with pytest.raises(ValueError, match="não encontrado"):
            op.execute(client_alias="CLIENTE_ATIVO", service_alias="SERVICO_DELETADO")

    def test_soft_delete_nonexistent_service_raises(self, repo):
        op = OpSoftDeleteService(repo, actor="Test")
        with pytest.raises(ValueError, match="não encontrado"):
            op.execute(client_alias="CLIENTE_ATIVO", service_alias="NAO_EXISTE")

    def test_soft_delete_service_audit_attr(self, repo):
        op = OpSoftDeleteService(repo, actor="TestAudit")
        assert op.audit_logger is not None


# ==============================================================================
# OpRestoreService — new
# ==============================================================================

class TestOpRestoreService:
    def test_restore_deleted_service(self, repo):
        op = OpRestoreService(repo, actor="Test")
        result = op.execute(client_alias="CLIENTE_ATIVO", service_alias="SERVICO_DELETADO")
        assert result["success"] is True
        assert "SERVICO_DELETADO" in result["message"]
        df = repo.get_services_dataframe()
        assert "SERVICO_DELETADO" in df['Alias'].values

    def test_restore_active_service_raises(self, repo):
        op = OpRestoreService(repo, actor="Test")
        with pytest.raises(ValueError, match="não está deletado"):
            op.execute(client_alias="CLIENTE_ATIVO", service_alias="SERVICO_ATIVO")

    def test_restore_nonexistent_service_raises(self, repo):
        op = OpRestoreService(repo, actor="Test")
        with pytest.raises(ValueError, match="não está deletado"):
            op.execute(client_alias="CLIENTE_ATIVO", service_alias="NAO_EXISTE")

    def test_restore_service_audit_attr(self, repo):
        op = OpRestoreService(repo, actor="TestAudit")
        assert op.audit_logger is not None


# ==============================================================================
# OpUpdateService — RULE-DOMAIN-2.4
# ==============================================================================

class TestOpUpdateService:
    def test_update_valid_field(self, repo):
        op = OpUpdateService(repo, actor="Test")
        result = op.execute(
            client_alias="CLIENTE_ATIVO", service_alias="SERVICO_ATIVO",
            field="Modalidade", value="Executivo"
        )
        assert result["success"] is True
        assert "Modalidade" in result["message"]
        df = repo.get_services_dataframe()
        updated = df[(df['AliasCliente'] == 'CLIENTE_ATIVO') & (df['Alias'] == 'SERVICO_ATIVO')]
        assert updated['Modalidade'].iloc[0] == 'Executivo'

    def test_update_invalid_field_raises(self, repo):
        op = OpUpdateService(repo, actor="Test")
        with pytest.raises(ValueError, match="Campo inválido"):
            op.execute(
                client_alias="CLIENTE_ATIVO", service_alias="SERVICO_ATIVO",
                field="CampoInexistente", value="X"
            )

    def test_update_nonexistent_service_raises(self, repo):
        op = OpUpdateService(repo, actor="Test")
        with pytest.raises(ValueError, match="não encontrado"):
            op.execute(
                client_alias="CLIENTE_ATIVO", service_alias="NAO_EXISTE",
                field="Modalidade", value="X"
            )

    def test_update_service_audit_attr(self, repo):
        op = OpUpdateService(repo, actor="TestAudit")
        assert op.audit_logger is not None


# ==============================================================================
# Backup verification — RULE-DOMAIN-2.1/2.3
# ==============================================================================

# ==============================================================================
# Edge cases
# ==============================================================================

class TestEdgeCases:
    def test_soft_delete_client_without_services(self, repo):
        op = OpSoftDeleteClient(repo, actor="Test")
        result = op.execute(alias="SEM_SERVICO")
        assert result["success"] is True

    def test_soft_delete_service_of_deleted_client(self, repo):
        op = OpSoftDeleteService(repo, actor="Test")
        result = op.execute(client_alias="CLIENTE_DELETADO", service_alias="SERV_ORFAO")
        assert result["success"] is True
