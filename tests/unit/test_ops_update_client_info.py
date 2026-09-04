import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from pathlib import Path
from foton_system.core.ops.audit_logger import AuditLogger


class TestOpUpdateClientInfoValidation:
    @patch('foton_system.core.ops.audit_logger.AuditLogger.log_event')
    def test_validate_rejects_empty_client_name(self, mock_log):
        from foton_system.core.ops.op_update_client_info import OpUpdateClientInfo
        op = OpUpdateClientInfo()
        with pytest.raises(ValueError, match="Client name is required"):
            op.execute(client_name="", section="Notas", content="teste")

    @patch('foton_system.core.ops.audit_logger.AuditLogger.log_event')
    def test_validate_rejects_empty_section(self, mock_log):
        from foton_system.core.ops.op_update_client_info import OpUpdateClientInfo
        op = OpUpdateClientInfo()
        with pytest.raises(ValueError, match="Section is required"):
            op.execute(client_name="ClienteX", section="  ", content="teste")

    @patch('foton_system.core.ops.audit_logger.AuditLogger.log_event')
    def test_validate_rejects_invalid_operation(self, mock_log):
        from foton_system.core.ops.op_update_client_info import OpUpdateClientInfo
        op = OpUpdateClientInfo()
        with pytest.raises(ValueError, match="Operação inválida"):
            op.execute(client_name="ClienteX", section="Notas", content="teste", operacao="delete")

    @patch('foton_system.core.ops.audit_logger.AuditLogger.log_event')
    def test_validate_rejects_field_without_campo(self, mock_log):
        from foton_system.core.ops.op_update_client_info import OpUpdateClientInfo
        op = OpUpdateClientInfo()
        with pytest.raises(ValueError, match="Campo is required for 'field' operation"):
            op.execute(client_name="ClienteX", section="areaTotal", content="100", operacao="field", campo="")


class TestOpUpdateClientInfoExecution:
    @patch('foton_system.modules.clients.application.use_cases.client_crud.update_client_info_file')
    @patch('foton_system.modules.clients.application.use_cases.client_query.resolve_client_path')
    @patch('foton_system.core.ops.audit_logger.AuditLogger.log_event')
    def test_execute_append_logs_audit(self, mock_log, mock_resolve, mock_update):
        mock_resolve.return_value = Path("/fake/cliente")
        mock_update.return_value = "INFO-cliente.md.bak.20260101"

        from foton_system.core.ops.op_update_client_info import OpUpdateClientInfo
        op = OpUpdateClientInfo(actor="TestAgent")
        result = op.execute(
            client_name="ClienteX",
            section="Notas",
            content="Nova anotação",
            operacao="append"
        )

        assert result["success"] is True
        assert result["client"] == "ClienteX"
        assert result["operacao"] == "append"
        mock_resolve.assert_called_once()
        mock_update.assert_called_once()
        mock_log.assert_called_once()

    @patch('foton_system.modules.clients.application.use_cases.client_crud.update_client_info_file')
    @patch('foton_system.modules.clients.application.use_cases.client_query.resolve_client_path')
    @patch('foton_system.core.ops.audit_logger.AuditLogger.log_event')
    def test_execute_replace_logs_audit(self, mock_log, mock_resolve, mock_update):
        mock_resolve.return_value = Path("/fake/cliente")
        mock_update.return_value = "INFO-cliente.md.bak.20260101"

        from foton_system.core.ops.op_update_client_info import OpUpdateClientInfo
        op = OpUpdateClientInfo()
        result = op.execute(
            client_name="ClienteX",
            section="Notas",
            content="Texto substituto",
            operacao="replace"
        )

        assert result["success"] is True
        assert result["operacao"] == "replace"
        mock_log.assert_called_once()

    @patch('foton_system.modules.clients.application.use_cases.client_crud.update_client_info_file')
    @patch('foton_system.modules.clients.application.use_cases.client_query.resolve_client_path')
    @patch('foton_system.core.ops.audit_logger.AuditLogger.log_event')
    def test_execute_remove_logs_audit(self, mock_log, mock_resolve, mock_update):
        mock_resolve.return_value = Path("/fake/cliente")
        mock_update.return_value = "INFO-cliente.md.bak.20260101"

        from foton_system.core.ops.op_update_client_info import OpUpdateClientInfo
        op = OpUpdateClientInfo()
        result = op.execute(
            client_name="ClienteX",
            section="Notas Antigas",
            content="",
            operacao="remove"
        )

        assert result["success"] is True
        assert result["operacao"] == "remove"
        mock_log.assert_called_once()

    @patch('foton_system.modules.clients.application.use_cases.client_crud.update_client_info_file')
    @patch('foton_system.modules.clients.application.use_cases.client_query.resolve_client_path')
    @patch('foton_system.core.ops.audit_logger.AuditLogger.log_event')
    def test_execute_field_logs_audit(self, mock_log, mock_resolve, mock_update):
        mock_resolve.return_value = Path("/fake/cliente")
        mock_update.return_value = "INFO-cliente.md.bak.20260101"

        from foton_system.core.ops.op_update_client_info import OpUpdateClientInfo
        op = OpUpdateClientInfo()
        result = op.execute(
            client_name="ClienteX",
            section="areaTotal",
            content="250",
            operacao="field",
            campo="areaTotal"
        )

        assert result["success"] is True
        assert result["operacao"] == "field"
        mock_log.assert_called_once()

    @patch('foton_system.modules.clients.application.use_cases.client_crud.update_client_info_file')
    @patch('foton_system.modules.clients.application.use_cases.client_query.resolve_client_path')
    @patch('foton_system.core.ops.audit_logger.AuditLogger.log_event')
    def test_execute_failure_still_logs_audit(self, mock_log, mock_resolve, mock_update):
        mock_resolve.side_effect = ValueError("Cliente 'Inexistente' não encontrado.")

        from foton_system.core.ops.op_update_client_info import OpUpdateClientInfo
        op = OpUpdateClientInfo()
        with pytest.raises(ValueError, match="não encontrado"):
            op.execute(client_name="Inexistente", section="Notas", content="teste")

        mock_log.assert_called_once()


class TestOpUpdateClientInfoIntegrationMCP:
    def test_mcp_adapter_uses_op_instead_of_direct_delegation(self):
        import inspect
        from foton_system.interfaces.mcp.mcp_services import MCPClientService

        source = inspect.getsource(MCPClientService.update_client_info)
        assert "OpUpdateClientInfo" in source, (
            "MCPClientService.update_client_info() must use OpUpdateClientInfo "
            "to ensure POP audit coverage"
        )