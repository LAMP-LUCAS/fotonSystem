"""
End-to-End Integration Tests for the Foton MCP.

These tests simulate the exact call chain that LLM agents (Claude, Gemini,
Qwen via mcp-hub) would use against the production binary. They verify
that ALL previously-broken tools now return valid responses.

Sprint 4 — E2E Validation
Author: Lucas Antonio (TDD discipline)
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd


# ==============================================================================
# E2E Test 1: Previously broken tools now work
# ==============================================================================

class TestPreviouslyBrokenToolsNowWork:
    """These are the EXACT tools that failed in production logs.

    Each test simulates the MCP call and verifies the tool returns
    a valid response (not an exception).
    """

    def test_pipeline_novo_cliente_factory_path(self, mock_config, temp_clients_dir):
        """pipeline_novo_cliente uses factory.get_client_service() (was Bug #1)."""
        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory
        from foton_system.interfaces.mcp.foton_mcp import _resolve_client_path

        # Bug #1 used to fail here: factory.get_client_service()
        factory = MCPServiceFactory.get_instance()
        service = factory.get_client_service()
        assert service is not None, "Factory must now provide get_client_service() (Bug #1 fix)"

        # Verify the helper works
        config = mock_config.return_value
        try:
            path = _resolve_client_path(config.base_pasta_clientes, "CLIENT_A", config)
        except AttributeError as e:
            if "get_client_service" in str(e):
                pytest.fail(f"REGRESSION Bug #1: {e}")
            raise
        assert path.name == "CLIENT_A"

    def test_validar_template_factory_path(self, mock_config, temp_clients_dir):
        """validar_template uses factory.get_client_service() (was Bug #1)."""
        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory

        factory = MCPServiceFactory.get_instance()
        # The exact line that used to fail: factory.get_client_service()
        service = factory.get_client_service()
        assert service is not None

    def test_sincronizar_base_no_dataframe_error(self, mock_config, temp_clients_dir):
        """sincronizar_base must NOT raise 'truth value ambiguous' (Bug #3)."""
        from foton_system.interfaces.mcp import foton_mcp

        # The MCP tool used to call `if result:` where result is a DataFrame
        try:
            result = foton_mcp.sincronizar_base()
        except ValueError as e:
            if "ambiguous" in str(e):
                pytest.fail(f"REGRESSION Bug #3 (DataFrame truth value): {e}")
            raise

        assert isinstance(result, str), f"sincronizar_base must return str, got {type(result).__name__}"
        # Must contain a count
        assert any(c.isdigit() for c in result), f"Result must contain a count: {result!r}"

    def test_cadastrar_cliente_uses_kwargs(self, mock_config, temp_clients_dir):
        """cadastrar_cliente must call service.create_client with kwargs (Bug #2)."""
        from foton_system.core.ops.op_create_client import OpCreateClient
        from foton_system.interfaces.mcp import foton_mcp

        with patch(
            "foton_system.core.ops.op_create_client.ExcelClientRepository"
        ) as MockRepo:
            repo = MagicMock()
            # Use a real DataFrame (pd.concat requires it; MagicMock breaks)
            repo.get_clients_dataframe.return_value = pd.DataFrame()
            MockRepo.return_value = repo

            # Pre-create folder to satisfy existence check
            (temp_clients_dir / "TST").mkdir(exist_ok=True)

            # This is the EXACT call from foton_mcp.py:226-232
            try:
                result = foton_mcp.cadastrar_cliente(
                    nome="E2E Test Client",
                    apelido="E2E",
                    nif="999",
                    email="e2e@test.com",
                    telefone="999999",
                )
            except TypeError as e:
                if "unexpected keyword" in str(e):
                    pytest.fail(f"REGRESSION Bug #2: kwargs not supported: {e}")
                raise

            assert isinstance(result, str)
            assert "✅" in result or "created" in result.lower() or "sucesso" in result.lower()

    def test_ler_ficha_cliente_works_via_factory(self, mock_config, temp_clients_dir):
        """ler_ficha_cliente uses _resolve_client_path (depends on Bug #1 fix)."""
        from foton_system.interfaces.mcp import foton_mcp

        result = foton_mcp.ler_ficha_cliente(cliente="CLIENT_B")
        assert isinstance(result, str)
        # Should find the INFO file
        assert "CLIENT B" in result or "CLIENT_B" in result, (
            f"ler_ficha_cliente must read the INFO file. Got: {result[:200]}"
        )

    def test_listar_servicos_cliente_works(self, mock_config, temp_clients_dir):
        """listar_servicos_cliente uses _resolve_client_path (depends on Bug #1 fix)."""
        from foton_system.interfaces.mcp import foton_mcp

        result = foton_mcp.listar_servicos_cliente(cliente="CLIENT_A")
        assert isinstance(result, str)
        assert "SERVICE_1" in result, (
            f"listar_servicos_cliente must list SERVICE_1. Got: {result[:200]}"
        )


# ==============================================================================
# E2E Test 2: Service layer (DRY) works correctly
# ==============================================================================

class TestServiceLayerDRY:
    """The MCP layer must delegate to the domain layer (DRY principle)."""

    def test_mcp_client_service_uses_real_client_service(self, mock_config, temp_clients_dir):
        """MCPClientService must wire to the real ClientService (no logic duplication)."""
        from foton_system.interfaces.mcp.mcp_services import (
            MCPServiceFactory,
            MCPClientService,
        )
        from foton_system.modules.clients.application.use_cases.client_service import (
            ClientService,
        )

        factory = MCPServiceFactory.get_instance()
        mcp_client_svc = factory.get_client_service()

        # Must be the new class
        assert isinstance(mcp_client_svc, MCPClientService), (
            f"Factory must return MCPClientService, got {type(mcp_client_svc).__name__}"
        )

        # Must wrap a real ClientService
        held = getattr(mcp_client_svc, "_client", None) or getattr(mcp_client_svc, "_service", None)
        assert held is not None, "MCPClientService must hold a reference to ClientService"
        assert isinstance(held, ClientService), (
            f"MCPClientService must wrap a real ClientService, got {type(held).__name__}"
        )
        assert "Mock" not in type(held).__name__, (
            "MCPClientService must not wrap a Mock (it must be a real ClientService)"
        )

    def test_fuzzy_match_works_through_mcp(self, mock_config, temp_clients_dir):
        """Fuzzy match must work via the MCP layer (delegated to ClientService)."""
        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory

        factory = MCPServiceFactory.get_instance()
        service = factory.get_client_service()

        # "CLIENT" is ambiguous (matches both CLIENT_A and CLIENT_B)
        # "CLIENT_A" is exact match
        path = service.resolve_client_path("CLIENT_A")
        assert path.name == "CLIENT_A"

    def test_resolve_nonexistent_raises_value_error(self, mock_config, temp_clients_dir):
        """Missing client must raise ValueError (not crash)."""
        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory

        factory = MCPServiceFactory.get_instance()
        service = factory.get_client_service()

        with pytest.raises(ValueError, match=r"n[ãa]o encontrad|not found"):
            service.resolve_client_path("DOES_NOT_EXIST")


# ==============================================================================
# E2E Test 3: Full tool flow smoke test
# ==============================================================================

class TestFullToolFlowSmoke:
    """Smoke test: import the MCP module and verify all tools are registered."""

    def test_all_mcp_tools_defined(self):
        """All expected MCP tools must be defined in the foton_mcp module."""
        from foton_system.interfaces.mcp import foton_mcp

        expected_tools = [
            "ping", "info_sistema", "listar_clientes", "cadastrar_cliente",
            "ler_ficha_cliente", "atualizar_ficha_cliente", "listar_servicos_cliente",
            "listar_documentos_cliente", "registrar_financeiro", "consultar_financeiro",
            "resumo_financeiro_geral", "listar_templates", "gerar_documento",
            "validar_template", "consultar_conhecimento", "indexar_conhecimento",
            "sincronizar_base", "sincronizar_clientes", "configurar_agente",
            "pipeline_novo_cliente", "pipeline_emitir_documento",
        ]

        missing = [name for name in expected_tools if not hasattr(foton_mcp, name)]
        assert not missing, f"Missing MCP tools in foton_mcp: {missing}"

        # All tools must be callable
        for name in expected_tools:
            tool = getattr(foton_mcp, name)
            assert callable(tool), f"MCP tool {name} is not callable"

    def test_mcp_server_instance_exists(self):
        """The FastMCP server instance must be constructible."""
        from foton_system.interfaces.mcp import foton_mcp

        assert foton_mcp.mcp is not None, "foton_mcp.mcp server instance must exist"
        # Server should have a name attribute (FastMCP protocol)
        assert hasattr(foton_mcp.mcp, "name"), "FastMCP server must have a name attribute"

    def test_mcp_module_imports_without_error(self):
        """The MCP module must import without errors (catches missing deps)."""
        try:
            import importlib
            from foton_system.interfaces.mcp import foton_mcp
            importlib.reload(foton_mcp)
        except Exception as e:
            pytest.fail(f"MCP module failed to import: {e}")
