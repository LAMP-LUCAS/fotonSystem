from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from datetime import datetime
import time
import pandas as pd

from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.shared.infrastructure.config.logger import setup_logger

logger = setup_logger()

# @story: STORY-014
# @rule: RULE-DOMAIN-3.1, RULE-DOMAIN-3.2, RULE-DOMAIN-3.3, RULE-DOMAIN-3.4, RULE-DOMAIN-3.5


@dataclass
class SyncReport:
    direcao: str = "bidir"
    dry_run: bool = True
    timestamp: str = ""
    clientes_novos: List[str] = field(default_factory=list)
    clientes_atualizados: List[str] = field(default_factory=list)
    clientes_deletados: List[str] = field(default_factory=list)
    servicos_novos: List[str] = field(default_factory=list)
    servicos_atualizados: List[str] = field(default_factory=list)
    conflitos: List[Dict[str, str]] = field(default_factory=list)
    erros: List[str] = field(default_factory=list)
    duracao_segundos: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "direcao": self.direcao,
            "dry_run": self.dry_run,
            "timestamp": self.timestamp,
            "duracao_segundos": self.duracao_segundos,
            "clientes_novos": self.clientes_novos,
            "clientes_atualizados": self.clientes_atualizados,
            "clientes_deletados": self.clientes_deletados,
            "servicos_novos": self.servicos_novos,
            "servicos_atualizados": self.servicos_atualizados,
            "conflitos": self.conflitos,
            "erros": self.erros,
            "total_novos": len(self.clientes_novos) + len(self.servicos_novos),
            "total_atualizados": len(self.clientes_atualizados) + len(self.servicos_atualizados),
            "total_erros": len(self.erros),
        }

    def resumo(self) -> str:
        lines = [f"Sync Report ({self.direcao})"]
        lines.append(f"  Timestamp: {self.timestamp}")
        lines.append(f"  Dry-run:   {self.dry_run}")
        lines.append(f"  Duracao:   {self.duracao_segundos}s")
        lines.append("")
        if self.clientes_novos:
            lines.append(f"  Clientes novos: {', '.join(self.clientes_novos)}")
        if self.clientes_atualizados:
            lines.append(f"  Clientes atualizados: {', '.join(self.clientes_atualizados)}")
        if self.clientes_deletados:
            lines.append(f"  Clientes deletados: {', '.join(self.clientes_deletados)}")
        if self.servicos_novos:
            lines.append(f"  Servicos novos: {', '.join(self.servicos_novos)}")
        if self.servicos_atualizados:
            lines.append(f"  Servicos atualizados: {', '.join(self.servicos_atualizados)}")
        if self.conflitos:
            lines.append(f"  Conflitos: {len(self.conflitos)}")
        if self.erros:
            lines.append(f"  Erros: {len(self.erros)}")
        lines.append("")
        total_novos = len(self.clientes_novos) + len(self.servicos_novos)
        total_atualizados = len(self.clientes_atualizados) + len(self.servicos_atualizados)
        if total_novos == 0 and total_atualizados == 0 and not self.erros:
            lines.append("  Nenhuma alteracao necessaria.")
        return "\n".join(lines)


def pipeline_sincronizacao(
    direcao: str = "bidir",
    dry_run: bool = True,
    repo: Any = None,
    config: Optional[Config] = None,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> SyncReport:
    """
    Unified sync pipeline for Clients and Services.

    Executes 5 sequential steps:
      1. snapshot  — capture current filesystem and DB state
      2. diff      — compare states to find differences
      3. validate  — check direction, invariants
      4. apply     — sync changes (only if dry_run=False)
      5. report    — build SyncReport with results

    Args:
        direcao: "pastas_to_db" | "db_to_pastas" | "bidir"
        dry_run: If True, only detect differences without applying (default True)
        repo: Optional repository override (for testing)
        config: Configuration object (uses default if None)

    Returns:
        SyncReport with consolidated results
    """
    config = config or Config()
    start_time = time.perf_counter()
    report = SyncReport(direcao=direcao, dry_run=dry_run)

    if repo is None:
        from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import (
            ExcelClientRepository,
        )
        from foton_system.modules.clients.application.use_cases.client_service import (
            ClientService,
        )
        repo = ExcelClientRepository(config)
        service = ClientService(repo, config)
    else:
        service = None

    if direcao not in ("pastas_to_db", "db_to_pastas", "bidir"):
        report.erros.append(f"Invalid direction: '{direcao}'. Use 'pastas_to_db', 'db_to_pastas', or 'bidir'.")
        report.duracao_segundos = time.perf_counter() - start_time
        return report

    try:
        if direcao in ("pastas_to_db", "bidir"):
            _step_pastas_to_db(repo, report, dry_run, service, progress_callback)

        if direcao in ("db_to_pastas", "bidir"):
            _step_db_to_pastas(repo, report, dry_run, service, config, progress_callback)

    except Exception as e:
        report.erros.append(str(e))
        logger.error(f"Pipeline sync failed: {e}")

    report.duracao_segundos = time.perf_counter() - start_time
    return report


# ---------------------------------------------------------------------------
# Step: snapshot + diff + validate + apply (pastas -> DB)
# ---------------------------------------------------------------------------

def _step_pastas_to_db(repo, report: SyncReport, dry_run: bool, service=None, progress_callback=None):
    """Snapshot folders, diff against DB, validate, apply if not dry_run."""
    # Snapshot: folders
    client_folders = repo.list_client_folders()
    db_clients = repo.get_clients_dataframe()
    db_aliases = set(db_clients["Alias"].dropna().values) if "Alias" in db_clients.columns else set()

    # Diff: find new clients
    for folder in sorted(client_folders):
        if folder not in db_aliases:
            report.clientes_novos.append(folder)

    # Validate: check for duplicate aliases across folders vs DB
    try:
        for folder in sorted(client_folders):
            db_current = repo.get_clients_dataframe()
            db_aliases_current = set(db_current["Alias"].dropna().values) if "Alias" in db_current.columns else set()
            if folder in db_aliases_current and folder not in db_aliases:
                # Conflict folders vs DB: filesystem prevails (RULE-3.5)
                report.conflitos.append({
                    "item": folder,
                    "tipo": "cliente",
                    "detail": "Folder exists but DB already has this alias. FS data will be used.",
                })

        # Apply: add new clients if not dry_run
        if not dry_run and report.clientes_novos:
            _apply_new_clients(repo, report, progress_callback)

        # Sync services
        _step_services_sync(repo, report, dry_run, progress_callback)
    except Exception as e:
        report.erros.append(f"pastas_to_db error: {e}")


def _apply_new_clients(repo, report: SyncReport, progress_callback=None):
    """Add newly detected clients to the database."""
    try:
        db_clients = repo.get_clients_dataframe()
        new_rows = []
        for alias in report.clientes_novos:
            new_rows.append({"Alias": alias, "NomeCliente": alias, "Status": "ATIVO"})
            if progress_callback:
                progress_callback(f"cliente:{alias}")
        if new_rows:
            new_df = pd.DataFrame(new_rows)
            updated = pd.concat([db_clients, new_df], ignore_index=True)
            repo.save_clients(updated)
            logger.info(f"Added {len(new_rows)} new clients to DB: {report.clientes_novos}")
    except Exception as e:
        report.erros.append(f"Failed to add new clients: {e}")


def _step_services_sync(repo, report: SyncReport, dry_run: bool, progress_callback=None):
    """Sync services: folders to DB."""
    try:
        client_folders = repo.list_client_folders()
        for client in sorted(client_folders):
            service_folders = repo.list_service_folders(client)
            if not service_folders:
                if progress_callback:
                    progress_callback(f"cliente:{client}")
                continue
            db_services = repo.get_services_dataframe()
            new_services = []
            for svc in sorted(service_folders):
                exists = False
                if not db_services.empty and "AliasCliente" in db_services.columns and "Alias" in db_services.columns:
                    mask = (db_services["AliasCliente"] == client) & (db_services["Alias"] == svc)
                    exists = mask.any()
                if not exists:
                    report.servicos_novos.append(f"{client}/{svc}")
                    new_services.append({"AliasCliente": client, "Alias": svc, "Status": "ATIVO"})
                if progress_callback:
                    progress_callback(f"servico:{client}/{svc}")

            if new_services and not dry_run:
                new_df = pd.DataFrame(new_services)
                updated = pd.concat([db_services, new_df], ignore_index=True)
                repo.save_services(updated)
                logger.info(f"Added {len(new_services)} new services for {client}")
    except Exception as e:
        report.erros.append(f"services sync error: {e}")


# ---------------------------------------------------------------------------
# Step: snapshot + diff + validate + apply (DB -> pastas)
# ---------------------------------------------------------------------------

def _step_db_to_pastas(repo, report: SyncReport, dry_run: bool, service=None, config=None, progress_callback=None):
    """Snapshot DB, diff folders, validate, apply if not dry_run."""
    try:
        # Snapshot: DB clients
        db_clients = repo.get_clients_dataframe()
        if db_clients.empty:
            return

        # Diff: find DB entries without folders
        for _, row in db_clients.iterrows():
            alias = row.get("Alias")
            if alias and not (repo.clients_dir / alias).exists() if hasattr(repo, "clients_dir") else True:
                folder_exists = False
                if hasattr(repo, "clients_dir"):
                    folder_exists = (repo.clients_dir / alias).exists()
                else:
                    try:
                        folder_exists = (config.base_pasta_clientes / alias).exists() if config else False
                    except Exception:
                        folder_exists = False

                if not folder_exists and alias not in report.clientes_atualizados:
                    report.clientes_atualizados.append(alias)

            if progress_callback:
                progress_callback(f"cliente:{alias}" if alias else "cliente:?")

        # Apply: create folders if not dry_run
        if not dry_run and report.clientes_atualizados:
            _apply_new_folders(repo, report, config, progress_callback)

        # Snapshot: DB services
        _step_db_services_to_pastas(repo, report, dry_run, config, progress_callback)
    except Exception as e:
        report.erros.append(f"db_to_pastas error: {e}")


def _step_db_services_to_pastas(repo, report: SyncReport, dry_run: bool, config=None, progress_callback=None):
    """Create service folders for DB entries that are missing folders."""
    try:
        db_services = repo.get_services_dataframe()
        if db_services.empty:
            return

        for _, row in db_services.iterrows():
            client_alias = row.get("AliasCliente")
            service_alias = row.get("Alias")
            if client_alias and service_alias:
                svc_key = f"{client_alias}/{service_alias}"
                if svc_key in report.servicos_atualizados:
                    continue

                folder_exists = False
                if hasattr(repo, "clients_dir"):
                    folder_exists = (repo.clients_dir / client_alias / service_alias).exists()
                else:
                    try:
                        folder_exists = (config.base_pasta_clientes / client_alias / service_alias).exists() if config else False
                    except Exception:
                        folder_exists = False

                if not folder_exists and svc_key not in report.servicos_atualizados:
                    report.servicos_atualizados.append(svc_key)

                if progress_callback:
                    progress_callback(f"servico:{svc_key}")

        # Apply: create folders if not dry_run
        if not dry_run and report.servicos_atualizados:
            for svc_key in report.servicos_atualizados:
                parts = svc_key.split("/", 1)
                if len(parts) == 2:
                    client_alias, service_alias = parts
                    try:
                        if hasattr(repo, "clients_dir"):
                            svc_path = repo.clients_dir / client_alias / service_alias
                        elif config:
                            svc_path = config.base_pasta_clientes / client_alias / service_alias
                        else:
                            continue
                        svc_path.mkdir(parents=True, exist_ok=True)
                        logger.info(f"Created folder for service: {svc_key}")
                        if progress_callback:
                            progress_callback(f"servico:{svc_key}")
                    except Exception as e:
                        report.erros.append(f"Failed to create folder for {svc_key}: {e}")
    except Exception as e:
        report.erros.append(f"db_services_to_pastas error: {e}")


def _apply_new_folders(repo, report: SyncReport, config=None, progress_callback=None):
    """Create folders for DB entries missing folders."""
    try:
        db_clients = repo.get_clients_dataframe()
        for _, row in db_clients.iterrows():
            alias = row.get("Alias")
            if alias and alias in report.clientes_atualizados:
                try:
                    if hasattr(repo, "clients_dir"):
                        client_path = repo.clients_dir / alias
                    elif config:
                        client_path = config.base_pasta_clientes / alias
                    else:
                        continue
                    client_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created folder for client: {alias}")
                    if progress_callback:
                        progress_callback(f"cliente:{alias}")
                except Exception as e:
                    report.erros.append(f"Failed to create folder for {alias}: {e}")
    except Exception as e:
        report.erros.append(f"apply new folders error: {e}")


def format_sync_report(report: SyncReport) -> str:
    """Alias for SyncReport.resumo() — backward compatibility."""
    return report.resumo()
