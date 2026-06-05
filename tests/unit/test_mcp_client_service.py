"""
Unit tests for MCPServiceFactory.get_client_service and MCPClientService.

Bug #1: 'MCPServiceFactory' object has no attribute 'get_client_service'
        foton_mcp.py:842 calls factory.get_client_service() but the
        factory only has get_finance_service, get_document_service,
        get_knowledge_service, and a private _get_path_resolver.

These tests assert the missing pieces:
- get_client_service() method exists and returns a service
- get_client_service() is a lazy singleton
- get_path_resolver() is a public method (called from MCP layer)
- MCPClientService class is importable from mcp_services
- MCPClientService delegates to a real ClientService (DRY)

TDD Phase: RED. Tests must fail against the current implementation.
"""

import inspect
import pytest
from pathlib import Path
from unittest.mock import Mock, patch


# ==============================================================================
# Test Group 1: get_client_service existence (Bug #1)
# ==============================================================================

class TestGetClientServiceExists:
    """The factory MUST expose get_client_service() — used by foton_mcp.py:842."""

    def test_factory_has_get_client_service_method(self):
        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory
        factory = MCPServiceFactory.get_instance()
        assert hasattr(factory, "get_client_service"), (
            "MCPServiceFactory MUST have get_client_service() method. "
            "foton_mcp.py:842 calls it and crashes with Bug #1."
        )
        assert callable(factory.get_client_service), (
            "get_client_service must be callable"
        )

    def test_get_client_service_returns_non_none(self):
        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory
        factory = MCPServiceFactory.get_instance()
        service = factory.get_client_service()
        assert service is not None, "get_client_service() must return a service instance"

    def test_get_client_service_is_lazy_singleton(self):
        """Repeated calls return the SAME instance (perf + consistency)."""
        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory
        factory = MCPServiceFactory.get_instance()
        svc1 = factory.get_client_service()
        svc2 = factory.get_client_service()
        assert svc1 is svc2, (
            "get_client_service() must return the same singleton instance on repeated calls"
        )

    def test_get_path_resolver_is_public(self):
        """foton_mcp.py uses the path resolver; it must be a public method."""
        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory
        factory = MCPServiceFactory.get_instance()
        assert hasattr(factory, "get_path_resolver"), (
            "Factory must expose get_path_resolver() as PUBLIC method "
            "(currently only _get_path_resolver exists)."
        )
        resolver = factory.get_path_resolver()
        assert resolver is not None


# ==============================================================================
# Test Group 2: MCPClientService class & behavior (DRY)
# ==============================================================================

class TestMCPClientServiceClass:
    """MCPClientService class must exist and implement the expected protocol."""

    def test_mcp_client_service_class_exists(self):
        """Importable from mcp_services module."""
        from foton_system.interfaces.mcp import mcp_services
        assert hasattr(mcp_services, "MCPClientService"), (
            "MCPClientService class must be defined in mcp_services module. "
            "This is the missing piece for the factory's get_client_service()."
        )
        assert inspect.isclass(mcp_services.MCPClientService), (
            "MCPClientService must be a class (not a function or instance)"
        )

    def test_mcp_client_service_has_resolve_client_path(self):
        """Used by _resolve_client_path helper in foton_mcp.py:842-843."""
        from foton_system.interfaces.mcp.mcp_services import MCPClientService
        assert hasattr(MCPClientService, "resolve_client_path"), (
            "MCPClientService must expose resolve_client_path() "
            "(called by _resolve_client_path in foton_mcp.py:843)"
        )
        assert callable(getattr(MCPClientService, "resolve_client_path", None))

    def test_mcp_client_service_delegates_to_domain(self, fake_client_repository):
        """MCPClientService MUST delegate to a real ClientService (DRY principle)."""
        from foton_system.interfaces.mcp.mcp_services import MCPClientService
        from foton_system.modules.clients.application.use_cases.client_service import (
            ClientService,
        )

        domain_service = ClientService(fake_client_repository())
        mcp_service = MCPClientService(domain_service)

        # DRY: the MCP service should hold a reference to the domain service
        assert hasattr(mcp_service, "_client") or hasattr(mcp_service, "_service"), (
            "MCPClientService must hold a reference to the underlying ClientService "
            "(attribute: _client or _service) to delegate work."
        )

        # The underlying instance must be a real ClientService
        held = getattr(mcp_service, "_client", None) or getattr(mcp_service, "_service", None)
        assert held is domain_service, (
            "MCPClientService must wrap the same ClientService instance (no duplication)"
        )

    def test_resolve_client_path_delegates_to_domain(self, fake_client_repository):
        """resolve_client_path MUST delegate (no logic duplication)."""
        from foton_system.interfaces.mcp.mcp_services import MCPClientService
        from pathlib import Path

        domain = fake_client_repository()
        service = ClientService_factory = None
        from foton_system.modules.clients.application.use_cases.client_service import (
            ClientService,
        )
        domain_service = ClientService(domain)

        expected_path = Path("/fake/clients/FOO")
        with patch.object(
            domain_service, "resolve_client_path", return_value=expected_path
        ) as mock_resolve:
            mcp_service = MCPClientService(domain_service)
            result = mcp_service.resolve_client_path("FOO")

        assert result == expected_path
        mock_resolve.assert_called_once_with("FOO")

    def test_resolve_client_path_propagates_value_error(self, fake_client_repository):
        """ValueError (client not found) must propagate as-is (MCP layer handles it)."""
        from foton_system.interfaces.mcp.mcp_services import MCPClientService
        from foton_system.modules.clients.application.use_cases.client_service import (
            ClientService,
        )

        domain_service = ClientService(fake_client_repository())
        mcp_service = MCPClientService(domain_service)

        with patch.object(
            domain_service, "resolve_client_path",
            side_effect=ValueError("Cliente não encontrado"),
        ):
            with pytest.raises(ValueError, match="Cliente não encontrado"):
                mcp_service.resolve_client_path("NONEXISTENT")


# ==============================================================================
# Test Group 3: Factory integration smoke
# ==============================================================================

class TestFactoryIntegrationSmoke:
    """The full chain: factory -> MCPClientService -> ClientService must work."""

    def test_factory_full_chain_returns_typed_service(self, mock_config, temp_clients_dir):
        """The chain must end in a real MCPClientService that wraps ClientService."""
        from foton_system.interfaces.mcp.mcp_services import (
            MCPServiceFactory,
            MCPClientService,
        )
        from foton_system.modules.clients.application.use_cases.client_service import (
            ClientService,
        )

        factory = MCPServiceFactory.get_instance()
        service = factory.get_client_service()

        assert isinstance(service, MCPClientService), (
            f"Factory must return MCPClientService, got {type(service).__name__}"
        )
        # And the wrapped domain service must be a real ClientService
        held = getattr(service, "_client", None) or getattr(service, "_service", None)
        assert isinstance(held, ClientService), (
            f"MCPClientService must wrap a real ClientService, got {type(held).__name__}"
        )

    def test_factory_full_chain_resolves_client(self, mock_config, temp_clients_dir):
        """End-to-end: factory -> service -> resolve real client folder."""
        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory

        factory = MCPServiceFactory.get_instance()
        service = factory.get_client_service()

        # CLIENT_A exists in temp_clients_dir
        path = service.resolve_client_path("CLIENT_A")
        assert path.name == "CLIENT_A", f"Expected CLIENT_A, got {path.name}"

    def test_factory_full_chain_fuzzy_match(self, mock_config, temp_clients_dir):
        """Fuzzy match must work via the delegated ClientService."""
        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory

        factory = MCPServiceFactory.get_instance()
        service = factory.get_client_service()

        # "CLIENT" is a substring of both CLIENT_A and CLIENT_B; should raise ValueError(ambiguous)
        with pytest.raises(ValueError, match=r"[Aa]mb[íi]gu|[Mm]ais espec"):
            service.resolve_client_path("CLIENT")
