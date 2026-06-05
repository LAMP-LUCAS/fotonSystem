"""
Unit tests for SyncService.sync_dashboard and sincronizar_base MCP tool.

Bug #3: sync_dashboard returns a DataFrame.
        The MCP tool foton_mcp.py:709 does `if result:` which raises
        "The truth value of a DataFrame is ambiguous" for non-empty frames.

These tests assert:
- sync_dashboard returns int (record count), NOT a DataFrame
- sincronizar_base MCP tool does NOT use bare `if result:` check
- Empty case (0 records) is handled without saying "no clients"
- Legitimate count > 0 is reported correctly

TDD Phase: RED. Tests must fail against the current implementation.
"""

import inspect
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


# ==============================================================================
# Test Group 1: sync_dashboard return type (Bug #3)
# ==============================================================================

class TestSyncDashboardReturnType:
    """sync_dashboard MUST return int (record count), never a DataFrame."""

    def test_sync_dashboard_return_annotation_is_int(self):
        from foton_system.modules.sync.sync_service import SyncService
        sig = inspect.signature(SyncService.sync_dashboard)
        # The annotation MUST be set AND must be int (not Signature.empty, not DataFrame)
        assert sig.return_annotation is not inspect.Signature.empty, (
            "sync_dashboard MUST have an explicit return annotation. "
            "Without one, callers cannot trust the return type. "
            "Bug #3 is masked by missing annotation."
        )
        assert sig.return_annotation in (int, "int"), (
            f"sync_dashboard return annotation must be int, got {sig.return_annotation}. "
            f"Returning a DataFrame causes Bug #3 at foton_mcp.py:709."
        )

    def test_sync_dashboard_returns_int_with_empty_dir(self, tmp_path):
        """With an empty clients dir, sync_dashboard must return 0 (int)."""
        from foton_system.modules.sync.sync_service import SyncService

        with patch("foton_system.modules.sync.sync_service.Config") as mock_cfg:
            mock_cfg.return_value.base_pasta_clientes = tmp_path
            mock_cfg.return_value.base_dados = tmp_path / "out.xlsx"

            service = SyncService()
            result = service.sync_dashboard()

        assert not hasattr(result, "columns"), (
            f"sync_dashboard must NOT return a DataFrame (Bug #3). "
            f"Got object with .columns attribute: {type(result).__name__}"
        )
        assert isinstance(result, int), (
            f"sync_dashboard must return int, got {type(result).__name__}: {result!r}"
        )
        assert result == 0, f"Expected 0 for empty dir, got {result}"

    def test_sync_dashboard_returns_int_with_clients(self, tmp_path):
        """With N clients, sync_dashboard must return N (int), not a DataFrame."""
        from foton_system.modules.sync.sync_service import SyncService

        # Create 2 fake clients with INFO-CLIENTE.md
        client_a = tmp_path / "ALICE"
        client_a.mkdir()
        (client_a / "INFO-CLIENTE.md").write_text(
            "@nomeCliente: ALICE\n@cpf: 111\n", encoding="utf-8"
        )

        client_b = tmp_path / "BOB"
        client_b.mkdir()
        (client_b / "INFO-CLIENTE.md").write_text(
            "@nomeCliente: BOB\n@cpf: 222\n", encoding="utf-8"
        )

        with patch("foton_system.modules.sync.sync_service.Config") as mock_cfg:
            mock_cfg.return_value.base_pasta_clientes = tmp_path
            mock_cfg.return_value.base_dados = tmp_path / "out.xlsx"

            service = SyncService()
            result = service.sync_dashboard()

        assert isinstance(result, int), (
            f"sync_dashboard must return int, got {type(result).__name__}"
        )
        assert result == 2, f"Expected 2 for 2 clients, got {result}"

    def test_sync_dashboard_does_not_return_dataframe(self, tmp_path):
        """REGRESSION TEST: ensure DataFrame return type is gone."""
        from foton_system.modules.sync.sync_service import SyncService
        import pandas as pd

        client = tmp_path / "JOAO"
        client.mkdir()
        (client / "INFO-CLIENTE.md").write_text(
            "@nomeCliente: JOAO\n", encoding="utf-8"
        )

        with patch("foton_system.modules.sync.sync_service.Config") as mock_cfg:
            mock_cfg.return_value.base_pasta_clientes = tmp_path
            mock_cfg.return_value.base_dados = tmp_path / "out.xlsx"

            service = SyncService()
            result = service.sync_dashboard()

        assert not isinstance(result, pd.DataFrame), (
            "REGRESSION: sync_dashboard must NOT return a DataFrame (Bug #3 root cause)"
        )


# ==============================================================================
# Test Group 2: sincronizar_base MCP tool — bare truth check (Bug #3)
# ==============================================================================

class TestSincronizarBaseMCPLayer:
    """The MCP tool must use explicit None/int check, NOT `if result:`."""

    def _get_sincronizar_base_source(self):
        from foton_system.interfaces.mcp import foton_mcp
        return inspect.getsource(foton_mcp.sincronizar_base)

    def test_no_bare_if_result_check(self):
        """foton_mcp.py:709 must not use bare `if result:` (causes Bug #3).

        The current source has: `return f"... Records: {len(result)}" if result else "..."`
        which is a bare truthy check on a DataFrame. Detect any of:
        - `if result:` (no comparator)
        - `if not result:` (conflates 0 with None)
        - `if result else ...` (inline ternary, same bug)
        - `... if result ...` (inline ternary with bare `if result`)
        """
        source = self._get_sincronizar_base_source()
        # Look for any bare truthy reference to `result`
        # Patterns: `if result:`, `if not result:`, `... if result else ...`
        forbidden = ["if result:", "if not result:", "if result else", "if not result else"]
        for pattern in forbidden:
            assert pattern not in source, (
                f"Bug #3 — bare truthy check '{pattern}' found in sincronizar_base source. "
                f"Use `if result is None` or `if result is not None` to handle the "
                f"DataFrame truth-value ambiguity (Bug #3 root cause)."
            )

    def test_uses_explicit_none_check(self):
        """foton_mcp.py:709 must distinguish 0 (empty) from None (error)."""
        source = self._get_sincronizar_base_source()
        assert "if result is None" in source or "if result is not None" in source, (
            "sincronizar_base must use explicit `is None` check (not `if result:`) "
            "to handle the DataFrame truth-value ambiguity."
        )

    def test_handles_legitimate_zero_count(self, tmp_path):
        """0 records is a valid empty result; must not raise / be treated as error."""
        from foton_system.interfaces.mcp import foton_mcp

        with patch("foton_system.modules.sync.sync_service.Config") as mock_cfg:
            mock_cfg.return_value.base_pasta_clientes = tmp_path
            mock_cfg.return_value.base_dados = tmp_path / "out.xlsx"

            result = foton_mcp.sincronizar_base()

        # Empty folder: 0 records is a legitimate outcome. The user
        # is informed ("No clients found.") but it must NOT be
        # reported as a sync error.
        assert "sync error" not in result.lower(), (
            f"sincronizar_base conflated 0 (empty) with error. Got: {result!r}"
        )
        # Either an empty-result message or a non-error string is OK;
        # what we forbid is the exception branch.
        assert isinstance(result, str) and len(result) > 0

    def test_handles_legitimate_positive_count(self, tmp_path):
        """A count > 0 must be reported, not crashed on DataFrame truth value."""
        from foton_system.interfaces.mcp import foton_mcp

        (tmp_path / "FOO").mkdir()
        (tmp_path / "FOO" / "INFO-CLIENTE.md").write_text(
            "@nomeCliente: FOO\n", encoding="utf-8"
        )

        with patch("foton_system.modules.sync.sync_service.Config") as mock_cfg:
            mock_cfg.return_value.base_pasta_clientes = tmp_path
            mock_cfg.return_value.base_dados = tmp_path / "out.xlsx"

            result = foton_mcp.sincronizar_base()

        # Bug #3 used to make this raise "truth value ambiguous" (caught by other tests)
        assert "ambiguous" not in result.lower(), (
            f"DataFrame truth value leaked to MCP layer: {result!r}"
        )
        # Must contain the count (1)
        assert "1" in result, f"Expected '1' in result, got: {result!r}"

    def test_does_not_raise_dataframe_ambiguous(self, tmp_path):
        """The real call must not raise the DataFrame truth-value error.

        Reproduces Bug #3: when sync_dashboard returns a non-empty DataFrame and
        the MCP layer does `if result:`, pandas raises
        'The truth value of a DataFrame is ambiguous'.
        """
        from foton_system.interfaces.mcp import foton_mcp

        # Add a client so sync_dashboard has data to process
        (tmp_path / "FOO").mkdir()
        (tmp_path / "FOO" / "INFO-CLIENTE.md").write_text(
            "@nomeCliente: FOO\n", encoding="utf-8"
        )

        with patch("foton_system.modules.sync.sync_service.Config") as mock_cfg:
            mock_cfg.return_value.base_pasta_clientes = tmp_path
            mock_cfg.return_value.base_dados = tmp_path / "out.xlsx"

            # The MCP tool must not propagate the DataFrame truth-value error
            try:
                result = foton_mcp.sincronizar_base()
            except ValueError as e:
                if "ambiguous" in str(e):
                    pytest.fail(
                        f"REGRESSION: DataFrame truth value error (Bug #3): {e}"
                    )
                raise
            # The call should return a string with a count
            assert isinstance(result, str)
            assert any(c.isdigit() for c in result), (
                f"Result must contain the record count, got: {result!r}"
            )
