"""
Integration tests for the MCP factory + foton_mcp.py integration.

These tests verify the MCP tool layer works against the factory.
Key checks:
- The factory has all services the MCP tools need
- _resolve_client_path (the helper) works end-to-end
- The MCP logger is configured (silent stdout, doesn't pollute LLM context)

TDD Phase: RED. Tests must fail against the current broken factory.
"""

import inspect
import pytest
import logging
from pathlib import Path
from unittest.mock import patch


class TestMCPLayerIntegration:
    """Tests that simulate the MCP tool layer using the factory."""

    def test_resolve_client_path_helper_works(self, mock_config, temp_clients_dir):
        """The _resolve_client_path helper in foton_mcp.py must not raise AttributeError."""
        from foton_system.interfaces.mcp.foton_mcp import _resolve_client_path

        config = mock_config.return_value
        # This used to fail: 'MCPServiceFactory' object has no attribute 'get_client_service'
        try:
            path = _resolve_client_path(config.base_pasta_clientes, "CLIENT_A", config)
        except AttributeError as e:
            if "get_client_service" in str(e):
                pytest.fail(
                    f"REGRESSION: Bug #1 — factory missing get_client_service(): {e}"
                )
            raise
        assert path.name == "CLIENT_A"

    def test_factory_exposes_all_required_services(self):
        """All services the MCP tool layer needs must be available."""
        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory

        factory = MCPServiceFactory.get_instance()

        for method in (
            "get_client_service",  # Bug #1 — missing
            "get_finance_service",
            "get_document_service",
            "get_knowledge_service",
            "get_path_resolver",  # Currently only _get_path_resolver
        ):
            assert hasattr(factory, method), (
                f"MCPServiceFactory.{method}() is required by the MCP tool layer"
            )
            assert callable(getattr(factory, method)), (
                f"MCPServiceFactory.{method} must be callable"
            )

    def test_logger_is_configured_silently(self):
        """The MCP logger must be set up (no StreamHandler to stdout).

        Why: the MCP server communicates over stdio, so any logger writing
        to stdout corrupts the JSON-RPC stream.
        """
        from foton_system.interfaces.mcp import foton_mcp

        assert hasattr(foton_mcp, "_logger"), "foton_mcp must define a _logger"
        assert isinstance(foton_mcp._logger, logging.Logger), (
            f"_logger must be a logging.Logger, got {type(foton_mcp._logger).__name__}"
        )

        # No StreamHandler pointing to stdout
        import sys
        for handler in foton_mcp._logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                assert handler.stream is not sys.stdout, (
                    "MCP _logger must NOT log to stdout (corrupts JSON-RPC stdio). "
                    f"Handler: {handler!r}"
                )

    def test_factory_singleton_preserved_across_calls(self):
        """The factory must preserve its singleton across get_instance() calls."""
        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory

        f1 = MCPServiceFactory.get_instance()
        f2 = MCPServiceFactory.get_instance()
        assert f1 is f2, "MCPServiceFactory must be a singleton"
