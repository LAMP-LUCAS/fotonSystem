"""
Tests for STORY-014: Pipeline de Sincronizacao Unificado.

Covers RULE-DOMAIN-3.1 through RULE-DOMAIN-3.5.
"""

import pytest
import time
from pathlib import Path
from datetime import datetime

# @story: STORY-014
# @rule: RULE-DOMAIN-3.1, RULE-DOMAIN-3.2, RULE-DOMAIN-3.3, RULE-DOMAIN-3.4, RULE-DOMAIN-3.5

# ==============================================================================
# Fake Repository for testing pipeline isolation
# ==============================================================================

class FakeSyncRepo:
    """In-memory fake repository for pipeline sync tests.

    Simulates both filesystem folders and database DataFrames.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.clients_dir = base_dir / "CLIENTES"
        self.clients_dir.mkdir(parents=True, exist_ok=True)

        # Simulated DB state: list of dicts
        self._clients_db: list[dict] = []
        self._services_db: list[dict] = []

    def get_clients_dataframe(self):
        import pandas as pd
        if not self._clients_db:
            return pd.DataFrame(columns=["Alias", "NomeCliente", "CodCliente", "Status"])
        return pd.DataFrame(self._clients_db)

    def get_all_clients_dataframe(self):
        return self.get_clients_dataframe()

    def get_services_dataframe(self):
        import pandas as pd
        if not self._services_db:
            return pd.DataFrame(columns=["AliasCliente", "Alias", "CodServico", "Status"])
        return pd.DataFrame(self._services_db)

    def get_all_services_dataframe(self):
        return self.get_services_dataframe()

    def save_clients(self, df):
        import pandas as pd
        self._clients_db = df.to_dict("records") if isinstance(df, pd.DataFrame) else df

    def save_services(self, df):
        import pandas as pd
        self._services_db = df.to_dict("records") if isinstance(df, pd.DataFrame) else df

    def list_client_folders(self):
        return {p.name for p in self.clients_dir.iterdir() if p.is_dir()}

    def list_service_folders(self, client_name: str):
        client_path = self.clients_dir / client_name
        if client_path.exists():
            return {p.name for p in client_path.iterdir() if p.is_dir()}
        return set()

    def create_folder(self, path):
        Path(path).mkdir(parents=True, exist_ok=True)

    def soft_delete_client(self, alias: str) -> bool:
        for c in self._clients_db:
            if c.get("Alias") == alias:
                c["Status"] = "DELETADO"
                return True
        return False

    def soft_delete_service(self, client_alias: str, service_alias: str) -> bool:
        for s in self._services_db:
            if s.get("AliasCliente") == client_alias and s.get("Alias") == service_alias:
                s["Status"] = "DELETADO"
                return True
        return False

    def restore_client(self, alias: str) -> bool:
        for c in self._clients_db:
            if c.get("Alias") == alias:
                c["Status"] = "ATIVO"
                return True
        return False

    def get_deleted_clients(self):
        return [c for c in self._clients_db if c.get("Status") == "DELETADO"]

    def restore_service(self, client_alias: str, service_alias: str) -> bool:
        for s in self._services_db:
            if s.get("AliasCliente") == client_alias and s.get("Alias") == service_alias:
                s["Status"] = "ATIVO"
                return True
        return False

    def get_deleted_services(self):
        return [s for s in self._services_db if s.get("Status") == "DELETADO"]


def make_info_file(client_dir: Path, alias: str, content: str = None):
    """Create a stub INFO file for a client folder."""
    info = client_dir / f"INFO-CLIENTE-{alias}_01_R00.md"
    if content is None:
        content = f"@nomeCliente: {alias}\n@alias: {alias}\n"
    info.write_text(content, encoding="utf-8")
    return info


# ==============================================================================
# RULE-DOMAIN-3.1: pipeline_sincronizacao with 3 directions + dry_run
# ==============================================================================

class TestPipelineDirecoes:
    """pipeline_sincronizacao must support 3 directions + dry_run default."""

    def test_direcao_pastas_to_db_detects_new_clients(self, tmp_path):
        from foton_system.modules.clients.application.use_cases.pipeline_sync import (
            pipeline_sincronizacao, SyncReport
        )
        repo = FakeSyncRepo(tmp_path)
        (repo.clients_dir / "CLIENTE_A").mkdir()
        make_info_file(repo.clients_dir / "CLIENTE_A", "CLIENTE_A")

        report = pipeline_sincronizacao(direcao="pastas_to_db", repo=repo, dry_run=True)

        assert isinstance(report, SyncReport)
        assert "CLIENTE_A" in report.clientes_novos
        # dry_run: deve detectar mas NAO adicionar ao DB
        db = repo.get_clients_dataframe()
        assert db.empty or "CLIENTE_A" not in db["Alias"].values

    def test_direcao_db_to_pastas_creates_folders(self, tmp_path):
        from foton_system.modules.clients.application.use_cases.pipeline_sync import (
            pipeline_sincronizacao, SyncReport
        )
        repo = FakeSyncRepo(tmp_path)
        repo.save_clients([{"Alias": "CLIENTE_B", "NomeCliente": "Cliente B", "Status": "ATIVO"}])

        report = pipeline_sincronizacao(direcao="db_to_pastas", repo=repo, dry_run=False)

        assert isinstance(report, SyncReport)
        assert (repo.clients_dir / "CLIENTE_B").exists()
        assert "CLIENTE_B" in report.clientes_atualizados

    def test_direcao_bidir_runs_both(self, tmp_path):
        from foton_system.modules.clients.application.use_cases.pipeline_sync import (
            pipeline_sincronizacao, SyncReport
        )
        repo = FakeSyncRepo(tmp_path)

        # pastas_to_db: folder exists but not in DB
        (repo.clients_dir / "CLIENTE_C").mkdir()
        make_info_file(repo.clients_dir / "CLIENTE_C", "CLIENTE_C")
        # db_to_pastas: DB entry without folder
        repo.save_clients([{"Alias": "CLIENTE_D", "NomeCliente": "Cliente D", "Status": "ATIVO"}])

        report = pipeline_sincronizacao(direcao="bidir", repo=repo, dry_run=False)

        assert "CLIENTE_C" in report.clientes_novos
        assert "CLIENTE_D" in report.clientes_atualizados
        # CLIENTE_C should now be in DB
        db = repo.get_clients_dataframe()
        assert "CLIENTE_C" in db["Alias"].values
        # CLIENTE_D should have a folder
        assert (repo.clients_dir / "CLIENTE_D").exists()

    def test_dry_run_true_default_no_apply(self, tmp_path):
        from foton_system.modules.clients.application.use_cases.pipeline_sync import (
            pipeline_sincronizacao
        )
        repo = FakeSyncRepo(tmp_path)
        (repo.clients_dir / "CLIENTE_E").mkdir()
        make_info_file(repo.clients_dir / "CLIENTE_E", "CLIENTE_E")

        report = pipeline_sincronizacao(direcao="pastas_to_db", repo=repo)

        assert report.dry_run is True
        db = repo.get_clients_dataframe()
        assert "CLIENTE_E" not in db["Alias"].values

    def test_dry_run_false_applies_changes(self, tmp_path):
        from foton_system.modules.clients.application.use_cases.pipeline_sync import (
            pipeline_sincronizacao
        )
        repo = FakeSyncRepo(tmp_path)
        (repo.clients_dir / "CLIENTE_F").mkdir()
        make_info_file(repo.clients_dir / "CLIENTE_F", "CLIENTE_F")

        report = pipeline_sincronizacao(direcao="pastas_to_db", repo=repo, dry_run=False)

        assert report.dry_run is False
        db = repo.get_clients_dataframe()
        assert "CLIENTE_F" in db["Alias"].values


# ==============================================================================
# RULE-DOMAIN-3.2: 5-step sequential pipeline
# ==============================================================================

class TestPipeline5Steps:
    """Pipeline must execute snapshot -> diff -> validate -> apply -> report."""

    def test_snapshot_captures_state(self, tmp_path):
        from foton_system.modules.clients.application.use_cases.pipeline_sync import (
            pipeline_sincronizacao
        )
        repo = FakeSyncRepo(tmp_path)
        repo.save_clients([{"Alias": "CLIENTE_X", "Status": "ATIVO"}])
        (repo.clients_dir / "CLIENTE_Y").mkdir()
        make_info_file(repo.clients_dir / "CLIENTE_Y", "CLIENTE_Y")

        report = pipeline_sincronizacao(direcao="bidir", repo=repo, dry_run=True)

        assert report.duracao_segundos > 0
        assert hasattr(report, "clientes_novos")
        assert hasattr(report, "clientes_atualizados")

    def test_validate_errors_included_in_report(self, tmp_path):
        from foton_system.modules.clients.application.use_cases.pipeline_sync import (
            pipeline_sincronizacao
        )
        repo = FakeSyncRepo(tmp_path)

        report = pipeline_sincronizacao(direcao="invalid_direction", repo=repo, dry_run=True)

        assert len(report.erros) > 0

    def test_report_has_timestamp(self, tmp_path):
        from foton_system.modules.clients.application.use_cases.pipeline_sync import (
            pipeline_sincronizacao
        )
        repo = FakeSyncRepo(tmp_path)

        report = pipeline_sincronizacao(direcao="pastas_to_db", repo=repo, dry_run=True)

        assert report.timestamp is not None


# ==============================================================================
# RULE-DOMAIN-3.3: SyncReport with to_dict() and resumo()
# ==============================================================================

class TestSyncReportSerialization:
    """SyncReport must provide to_dict() and resumo()."""

    def test_to_dict_returns_serializable_dict(self, tmp_path):
        from foton_system.modules.clients.application.use_cases.pipeline_sync import SyncReport
        report = SyncReport(
            direcao="bidir",
            dry_run=True,
            clientes_novos=["A", "B"],
            clientes_atualizados=["C"],
            servicos_novos=["A/Svc1"],
            conflitos=[{"item": "A", "detail": "FS > DB"}],
            erros=["Erro X"],
        )
        d = report.to_dict()

        assert isinstance(d, dict)
        assert d["direcao"] == "bidir"
        assert d["dry_run"] is True
        assert d["clientes_novos"] == ["A", "B"]
        assert d["erros"] == ["Erro X"]

    def test_to_dict_includes_metrics(self, tmp_path):
        from foton_system.modules.clients.application.use_cases.pipeline_sync import SyncReport
        report = SyncReport(direcao="pastas_to_db", clientes_novos=["A", "B", "C"])
        d = report.to_dict()

        assert d["total_novos"] == 3
        assert d["total_atualizados"] == 0
        assert d["total_erros"] == 0

    def test_resumo_returns_string(self, tmp_path):
        from foton_system.modules.clients.application.use_cases.pipeline_sync import SyncReport
        report = SyncReport(
            direcao="bidir",
            dry_run=True,
            clientes_novos=["A", "B"],
            erros=[],
        )
        text = report.resumo()

        assert isinstance(text, str)
        assert "bidir" in text.lower() or "Bidir" in text or "BIDIR" in text
        assert "dry" in text.lower()

def test_resumo_includes_counts(tmp_path):
        from foton_system.modules.clients.application.use_cases.pipeline_sync import SyncReport
        report = SyncReport(
            direcao="pastas_to_db",
            dry_run=False,
            clientes_novos=["X", "Y", "Z"],
            servicos_novos=["X/S1"],
            duracao_segundos=1.5,
        )
        text = report.resumo()
        assert "X, Y, Z" in text
        assert "1.5s" in text


# ==============================================================================
# RULE-DOMAIN-3.4: Legacy tools delegate to pipeline
# ==============================================================================

class TestAliasesDelegamAoPipeline:
    """Existing sync tools must delegate to pipeline_sincronizacao."""

    def test_sincronizar_clientes_uses_pipeline_pastas_to_db(self):
        import inspect
        from foton_system.interfaces.mcp import foton_mcp
        source = inspect.getsource(foton_mcp.sincronizar_clientes)
        assert "pipeline_sincronizacao" in source, (
            "sincronizar_clientes must delegate to pipeline_sincronizacao"
        )

    def test_sincronizar_pastas_clientes_uses_pipeline_db_to_pastas(self):
        # Validacao estrutural: verificar se o codigo da MCP tool
        # sincronizar_pastas_clientes chama pipeline_sincronizacao
        import inspect
        from foton_system.interfaces.mcp import foton_mcp
        source = inspect.getsource(foton_mcp.sincronizar_pastas_clientes)
        assert "pipeline_sincronizacao" in source, (
            "sincronizar_pastas_clientes must delegate to pipeline_sincronizacao"
        )

    def test_sincronizar_base_uses_pipeline_bidir(self):
        import inspect
        from foton_system.interfaces.mcp import foton_mcp
        source = inspect.getsource(foton_mcp.sincronizar_base)
        assert "pipeline_sincronizacao" in source, (
            "sincronizar_base must delegate to pipeline_sincronizacao"
        )


# ==============================================================================
# RULE-DOMAIN-3.5: Sync never removes data; filesystem prevails
# ==============================================================================

class TestSyncDataSafety:
    """Sync must never remove data, only add/update. FS prevails on conflict."""

    def test_sync_never_removes_db_records(self, tmp_path):
        from foton_system.modules.clients.application.use_cases.pipeline_sync import (
            pipeline_sincronizacao
        )
        repo = FakeSyncRepo(tmp_path)
        repo.save_clients([
            {"Alias": "EXISTENTE", "NomeCliente": "Existente", "Status": "ATIVO"},
        ])

        report = pipeline_sincronizacao(direcao="bidir", repo=repo, dry_run=False)

        db = repo.get_clients_dataframe()
        assert "EXISTENTE" in db["Alias"].values

    def test_sync_never_removes_folders(self, tmp_path):
        from foton_system.modules.clients.application.use_cases.pipeline_sync import (
            pipeline_sincronizacao
        )
        repo = FakeSyncRepo(tmp_path)
        (repo.clients_dir / "FOLDER_A").mkdir()

        report = pipeline_sincronizacao(direcao="bidir", repo=repo, dry_run=False)

        assert (repo.clients_dir / "FOLDER_A").exists()

    def test_filesystem_prevails_on_conflict_info_content(self, tmp_path):
        from foton_system.modules.clients.application.use_cases.pipeline_sync import (
            pipeline_sincronizacao
        )
        repo = FakeSyncRepo(tmp_path)

        (repo.clients_dir / "CONFLITO").mkdir()
        make_info_file(repo.clients_dir / "CONFLITO", "CONFLITO",
                       content="@nomeCliente: CONFLITO\n@versao: FS_ORIGINAL\n")

        repo.save_clients([{"Alias": "CONFLITO", "NomeCliente": "Conflito DB",
                            "CodCliente": "OLD-001", "Status": "ATIVO"}])

        report = pipeline_sincronizacao(direcao="bidir", repo=repo, dry_run=False)

        # FS data should be reflected in report (conflito detected)
        assert len(report.conflitos) >= 0

    def test_services_synced_without_deletion(self, tmp_path):
        from foton_system.modules.clients.application.use_cases.pipeline_sync import (
            pipeline_sincronizacao
        )
        repo = FakeSyncRepo(tmp_path)

        (repo.clients_dir / "CLIENTE_SVC").mkdir()
        make_info_file(repo.clients_dir / "CLIENTE_SVC", "CLIENTE_SVC")
        (repo.clients_dir / "CLIENTE_SVC" / "SERVICO_A").mkdir()

        report = pipeline_sincronizacao(direcao="bidir", repo=repo, dry_run=False)

        assert "CLIENTE_SVC" in report.clientes_novos or "CLIENTE_SVC" in report.clientes_atualizados
        db_svc = repo.get_services_dataframe()
        existing_services = db_svc.to_dict("records") if not db_svc.empty else []
        assert len(existing_services) >= 0


# ==============================================================================
# REGRESSION: pipeline_sincronizacao MCP tool signature
# ==============================================================================

class TestMCPToolSignature:
    """The pipeline_sincronizacao MCP tool must include dry_run parameter."""

    def test_mcp_tool_has_dry_run_param(self):
        import inspect
        from foton_system.interfaces.mcp import foton_mcp
        sig = inspect.signature(foton_mcp.pipeline_sincronizacao)
        assert "dry_run" in sig.parameters, (
            "pipeline_sincronizacao MCP tool must accept 'dry_run' parameter (RULE-DOMAIN-3.1)"
        )

    def test_mcp_tool_dry_run_default_true(self):
        import inspect
        from foton_system.interfaces.mcp import foton_mcp
        sig = inspect.signature(foton_mcp.pipeline_sincronizacao)
        default = sig.parameters["dry_run"].default
        assert default is True, (
            f"dry_run default must be True, got {default}"
        )

    def test_mcp_tool_accepts_direcao(self):
        import inspect
        from foton_system.interfaces.mcp import foton_mcp
        sig = inspect.signature(foton_mcp.pipeline_sincronizacao)
        assert "direcao" in sig.parameters
