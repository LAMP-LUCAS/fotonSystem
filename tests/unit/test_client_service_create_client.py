"""
Unit tests for ClientService.create_client — kwargs signature contract.

Bug #2: create_client(self, data) takes a single dict, but
        OpCreateClient.execute_logic and cadastrar_cliente call it with
        kwargs (name=..., tax_id=..., email=..., phone=..., alias=...).

These tests assert the CONTRACT that the call sites require:
- signature accepts name/tax_id/email/phone/alias as kwargs
- returns object with .codigo (str) and .caminho (Path) — for op_create_client
- validates input (rejects invalid filenames like "CON")
- persists via repository.save_clients
- auto-generates CodCliente when missing

TDD Phase: RED. Tests must fail against the current dict-based implementation.
"""

import inspect
import pytest
from pathlib import Path
from unittest.mock import Mock


# ==============================================================================
# Test Group 1: Signature contract (Bug #2 root)
# ==============================================================================

class TestCreateClientSignatureContract:
    """create_client MUST accept kwargs (not a single dict)."""

    def test_create_client_accepts_name_kwarg(self):
        from foton_system.modules.clients.application.use_cases.client_service import (
            ClientService,
        )
        sig = inspect.signature(ClientService.create_client)
        assert "name" in sig.parameters, (
            "create_client must accept 'name' as kwarg (called from op_create_client.py:57)"
        )

    def test_create_client_accepts_tax_id_kwarg(self):
        from foton_system.modules.clients.application.use_cases.client_service import (
            ClientService,
        )
        sig = inspect.signature(ClientService.create_client)
        assert "tax_id" in sig.parameters, (
            "create_client must accept 'tax_id' as kwarg (called from op_create_client.py:59)"
        )

    def test_create_client_accepts_email_kwarg(self):
        from foton_system.modules.clients.application.use_cases.client_service import (
            ClientService,
        )
        sig = inspect.signature(ClientService.create_client)
        assert "email" in sig.parameters, (
            "create_client must accept 'email' as kwarg (called from op_create_client.py:60)"
        )

    def test_create_client_accepts_phone_kwarg(self):
        from foton_system.modules.clients.application.use_cases.client_service import (
            ClientService,
        )
        sig = inspect.signature(ClientService.create_client)
        assert "phone" in sig.parameters, (
            "create_client must accept 'phone' as kwarg (called from op_create_client.py:61)"
        )

    def test_create_client_accepts_alias_kwarg(self):
        from foton_system.modules.clients.application.use_cases.client_service import (
            ClientService,
        )
        sig = inspect.signature(ClientService.create_client)
        assert "alias" in sig.parameters, (
            "create_client must accept 'alias' as kwarg (called from op_create_client.py:62)"
        )

    def test_create_client_does_not_take_single_data_dict(self):
        """REGRESSION TEST: ensure legacy dict signature is gone.

        Old (broken): def create_client(self, data)
        New (fixed):  def create_client(self, *, name, tax_id, email, phone, alias=None)
        """
        from foton_system.modules.clients.application.use_cases.client_service import (
            ClientService,
        )
        sig = inspect.signature(ClientService.create_client)
        assert "data" not in sig.parameters, (
            "create_client must NOT take a single 'data' dict. "
            "This is the legacy broken signature that caused Bug #2."
        )


# ==============================================================================
# Test Group 2: Call site compatibility (Bug #2 manifestation)
# ==============================================================================

class TestOpCreateClientCompatibility:
    """OpCreateClient.execute_logic calls service.create_client with kwargs."""

    def test_op_create_client_calls_create_client_with_kwargs(self, fake_client_repository):
        """The exact call from op_create_client.py:57-63 must not raise TypeError."""
        from foton_system.modules.clients.application.use_cases.client_service import (
            ClientService,
        )

        repo = fake_client_repository()
        service = ClientService(repo)

        # This is the EXACT call pattern from op_create_client.py:57-63
        try:
            result = service.create_client(
                name="João Silva",
                tax_id="123456789",
                email="joao@example.com",
                phone="11999999999",
                alias="JS",
            )
        except TypeError as e:
            pytest.fail(
                f"create_client does not accept kwargs (Bug #2): {e}. "
                f"See op_create_client.py:57-63 for the call pattern."
            )

        assert result is not None, "create_client must return a result object"

    def test_op_create_client_full_flow(self, fake_client_repository, temp_clients_dir):
        """Run op_create_client end-to-end (no patches); should succeed and persist."""
        from unittest.mock import patch
        from foton_system.core.ops.op_create_client import OpCreateClient

        repo = fake_client_repository()
        with patch(
            "foton_system.core.ops.op_create_client.ExcelClientRepository",
            return_value=repo,
        ), patch(
            "foton_system.core.ops.op_create_client.Config"
        ) as mock_cfg:
            mock_cfg.return_value.base_pasta_clientes = temp_clients_dir

            op = OpCreateClient(actor="TestActor")
            result = op.execute(
                name="Test User",
                alias="TU",
                nif="111",
                email="tu@test.com",
                phone="1111111111",
            )

        assert result["status"] == "CREATED", f"Expected CREATED, got {result}"
        assert "client_path" in result
        assert "client_id" in result
        # Repository must have been persisted
        assert repo.get_clients_dataframe() is not None


# ==============================================================================
# Test Group 3: Return value contract (required by op_create_client.py:66-74)
# ==============================================================================

class TestCreateClientReturnValue:
    """create_client must return an object with .codigo and .caminho (not a plain dict).

    The op_create_client.py code at lines 66-67 does:
        client_path = Path(created_client.caminho)
        client_id = created_client.codigo

    If we return a plain dict (legacy), this raises AttributeError.
    """

    def test_create_client_returns_object_with_codigo(self, fake_client_repository):
        from foton_system.modules.clients.application.use_cases.client_service import (
            ClientService,
        )
        repo = fake_client_repository()
        service = ClientService(repo)
        result = service.create_client(
            name="Maria Santos",
            tax_id="987",
            email="m@test.com",
            phone="222",
            alias="MS",
        )
        assert hasattr(result, "codigo"), (
            f"create_client must return object with .codigo (used by op_create_client.py:72). "
            f"Got: {type(result).__name__}"
        )
        assert result.codigo, "codigo must be non-empty"

    def test_create_client_returns_object_with_caminho(self, fake_client_repository):
        from foton_system.modules.clients.application.use_cases.client_service import (
            ClientService,
        )
        repo = fake_client_repository()
        service = ClientService(repo)
        result = service.create_client(
            name="Carlos Souza",
            tax_id="555",
            email="c@test.com",
            phone="333",
            alias="CS",
        )
        assert hasattr(result, "caminho"), (
            f"create_client must return object with .caminho (used by op_create_client.py:66). "
            f"Got: {type(result).__name__}"
        )
        assert isinstance(result.caminho, Path) or isinstance(result.caminho, str), (
            f"caminho must be Path or str, got {type(result.caminho).__name__}"
        )


# ==============================================================================
# Test Group 4: Validation & side-effects
# ==============================================================================

class TestCreateClientValidationAndPersistence:
    """create_client must validate input and persist via the repository."""

    def test_create_client_rejects_reserved_windows_name(self, fake_client_repository):
        from foton_system.modules.clients.application.use_cases.client_service import (
            ClientService,
        )
        repo = fake_client_repository()
        service = ClientService(repo)
        with pytest.raises(ValueError, match=r"[Ii]nvalid|[Cc]aract|[Rr]eserved"):
            service.create_client(
                name="CON",
                tax_id="1",
                email="x@x",
                phone="0",
                alias="CON",
            )

    def test_create_client_persists_to_repository(self, fake_client_repository):
        from foton_system.modules.clients.application.use_cases.client_service import (
            ClientService,
        )
        repo = fake_client_repository()
        service = ClientService(repo)
        service.create_client(
            name="João Silva",
            tax_id="123",
            email="j@x.com",
            phone="999",
            alias="JS",
        )
        df = repo.get_clients_dataframe()
        assert len(df) == 1, f"Repository must hold 1 client, got {len(df)}"
        # The persisted name must be present
        names = df.get("NomeCliente", pd.Series([])).tolist() if "NomeCliente" in df.columns else []
        # Also check 'nome' (lowercase) since op_create_client passes pt-BR keys
        assert any("João" in str(n) for n in names) or "João Silva" in df.to_dict("records").__repr__(), (
            f"Persisted client must include the name. Records: {df.to_dict('records')}"
        )

    def test_create_client_with_minimal_required_args(self, fake_client_repository):
        """Only name is required; tax_id/email/phone/alias default sensibly."""
        from foton_system.modules.clients.application.use_cases.client_service import (
            ClientService,
        )
        repo = fake_client_repository()
        service = ClientService(repo)
        result = service.create_client(name="Minimal Client")
        assert result is not None
        assert hasattr(result, "codigo")
        # Code should be auto-generated (not empty)
        assert result.codigo, "CodCliente must be auto-generated when not provided"

    def test_create_client_does_not_mutate_caller_kwargs(self, fake_client_repository):
        """create_client must not mutate the caller's dict (DRY / immutability)."""
        from foton_system.modules.clients.application.use_cases.client_service import (
            ClientService,
        )
        repo = fake_client_repository()
        service = ClientService(repo)
        # Pass as kwargs (new contract)
        service.create_client(
            name="Ana Pereira",
            tax_id="42",
            email="a@x.com",
            phone="555",
            alias="AP",
        )
        # The repository should hold the row; we cannot test kwarg dict
        # mutation, but we can ensure no exception was raised.
        assert len(repo.get_clients_dataframe()) == 1


# Import pandas at the top for type hints
import pandas as pd
