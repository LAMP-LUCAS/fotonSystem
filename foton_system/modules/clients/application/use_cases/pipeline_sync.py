from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import time

from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.shared.infrastructure.config.logger import setup_logger

logger = setup_logger()


@dataclass
class SyncReport:
    clientes_novos: List[str] = field(default_factory=list)
    clientes_atualizados: List[str] = field(default_factory=list)
    clientes_deletados: List[str] = field(default_factory=list)
    servicos_novos: List[str] = field(default_factory=list)
    servicos_atualizados: List[str] = field(default_factory=list)
    conflitos: List[Dict[str, str]] = field(default_factory=list)
    erros: List[str] = field(default_factory=list)
    duracao_segundos: float = 0.0


def pipeline_sincronizacao(direcao: str = "bidir", config: Optional[Config] = None) -> SyncReport:
    """
    Unified sync pipeline for Clients and Services.
    
    Args:
        direcao: "pastas_to_db" | "db_to_pastas" | "bidir"
        config: Configuration object (uses default if None)
    
    Returns:
        SyncReport with consolidated results
    """
    config = config or Config()
    start_time = time.perf_counter()
    report = SyncReport()
    
    try:
        from foton_system.modules.clients.application.use_cases.client_service import ClientService
        from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import ExcelClientRepository
        
        repo = ExcelClientRepository(config)
        service = ClientService(repo, config)
        
        if direcao in ("pastas_to_db", "bidir"):
            _sync_pastas_to_db(service, repo, report)
        
        if direcao in ("db_to_pastas", "bidir"):
            _sync_db_to_pastas(service, repo, report)
        
    except Exception as e:
        report.erros.append(str(e))
        logger.error(f"Pipeline sync failed: {e}")
    
    report.duracao_segundos = round(time.perf_counter() - start_time, 2)
    return report


def _sync_pastas_to_db(service, repo, report: SyncReport):
    """Sync: Discover new folders -> add to database."""
    try:
        client_folders = repo.list_client_folders()
        db_clients = repo.get_clients_dataframe()
        db_aliases = set(db_clients['Alias'].dropna().values) if 'Alias' in db_clients.columns else set()
        
        for folder in client_folders:
            if folder not in db_aliases:
                report.clientes_novos.append(folder)
                try:
                    repo.save_clients(pd.concat([db_clients, pd.DataFrame([{'Alias': folder, 'NomeCliente': folder, 'Status': 'ATIVO'}])], ignore_index=True))
                except Exception as e:
                    report.erros.append(f"Failed to add client {folder}: {e}")
        
        # Sync services
        for client in client_folders:
            service_folders = repo.list_service_folders(client)
            db_services = repo.get_services_dataframe()
            
            for svc in service_folders:
                exists = ((db_services['AliasCliente'] == client) & (db_services['Alias'] == svc)).any()
                if not exists:
                    report.servicos_novos.append(f"{client}/{svc}")
    except Exception as e:
        report.erros.append(f"pastas_to_db error: {e}")


def _sync_db_to_pastas(service, repo, report: SyncReport):
    """Sync: Ensure DB folders exist for all clients/services."""
    try:
        db_clients = repo.get_clients_dataframe()
        for _, row in db_clients.iterrows():
            alias = row.get('Alias')
            if alias and not (repo.base_pasta_clientes / alias).exists():
                repo.create_folder(repo.base_pasta_clientes / alias)
                report.clientes_atualizados.append(alias)
        
        db_services = repo.get_services_dataframe()
        for _, row in db_services.iterrows():
            client_alias = row.get('AliasCliente')
            service_alias = row.get('Alias')
            if client_alias and service_alias:
                service_path = repo.base_pasta_clientes / client_alias / service_alias
                if not service_path.exists():
                    repo.create_folder(service_path)
                    report.servicos_atualizados.append(f"{client_alias}/{service_alias}")
    except Exception as e:
        report.erros.append(f"db_to_pastas error: {e}")


def format_sync_report(report: SyncReport) -> str:
    """Format SyncReport as human-readable string."""
    lines = [f"📊 Relatório de Sincronização ({report.duracao_segundos}s)\n"]
    
    if report.clientes_novos:
        lines.append(f"  ✅ Clientes novos: {', '.join(report.clientes_novos)}")
    if report.clientes_atualizados:
        lines.append(f"  🔄 Clientes atualizados: {', '.join(report.clientes_atualizados)}")
    if report.clientes_deletados:
        lines.append(f"  🗑️  Clientes deletados: {', '.join(report.clientes_deletados)}")
    if report.servicos_novos:
        lines.append(f"  ✅ Serviços novos: {', '.join(report.servicos_novos)}")
    if report.servicos_atualizados:
        lines.append(f"  🔄 Serviços atualizados: {', '.join(report.servicos_atualizados)}")
    if report.conflitos:
        lines.append(f"  ⚠️  Conflitos: {len(report.conflitos)}")
    if report.erros:
        lines.append(f"  ❌ Erros: {len(report.erros)}")
    
    if not any([report.clientes_novos, report.clientes_atualizados, report.servicos_novos, report.servicos_atualizados]):
        lines.append("  ✅ Nenhuma alteração necessária.")
    
    return "\n".join(lines)


# Import pandas for _sync_pastas_to_db
import pandas as pd