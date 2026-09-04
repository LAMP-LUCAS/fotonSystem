"""
Servico de migracao e sincronizacao bidirecional entre Excel e SQLite.
Permite transicao suave sem perda de historico.
"""

from pathlib import Path
from typing import Dict, Any
import pandas as pd

from foton_system.modules.shared.infrastructure.database.sqlite_client_repository import SQLiteClientRepository
from foton_system.modules.shared.infrastructure.config.logger import setup_logger

logger = setup_logger()


class SQLiteMigrationService:
    @staticmethod
    def migrate_from_excel(excel_path: Path, sqlite_repo: SQLiteClientRepository) -> Dict[str, Any]:
        """
        Le baseDados.xlsx e insere todos os registros no SQLite.
        Operacao transacional e idempotente.
        """
        if not excel_path.exists():
            return {
                "success": False,
                "message": f"Arquivo Excel nao encontrado: {excel_path}",
                "clients_migrated": 0,
                "services_migrated": 0,
            }

        try:
            clients_migrated = 0
            services_migrated = 0

            with pd.ExcelFile(excel_path) as xls:
                # 1. Migra Clientes
                if "Clientes" in xls.sheet_names:
                    df_clients = pd.read_excel(xls, sheet_name="Clientes")
                    sqlite_repo.save_clients(df_clients)
                    clients_migrated = len(df_clients)

                # 2. Migra Servicos
                if "Servicos" in xls.sheet_names:
                    df_services = pd.read_excel(xls, sheet_name="Servicos")
                    sqlite_repo.save_services(df_services)
                    services_migrated = len(df_services)

            logger.info(
                f"Migracao Excel -> SQLite concluida com sucesso. Clientes: {clients_migrated}, Servicos: {services_migrated}"
            )

            return {
                "success": True,
                "message": "Migração concluída com sucesso.",
                "clients_migrated": clients_migrated,
                "services_migrated": services_migrated,
            }
        except Exception as e:
            logger.error(f"Erro na migracao Excel -> SQLite: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Falha na migração: {e}",
                "clients_migrated": 0,
                "services_migrated": 0,
            }

    @staticmethod
    def export_to_excel(sqlite_repo: SQLiteClientRepository, target_excel_path: Path) -> bool:
        """
        Exporta snapshot completo do SQLite para arquivo Excel formatado.
        Mantem interoperabilidade com ferramentas legadas de planilhas.
        """
        try:
            target_excel_path.parent.mkdir(parents=True, exist_ok=True)
            df_clients = sqlite_repo.get_all_clients_dataframe()
            df_services = sqlite_repo.get_all_services_dataframe()

            with pd.ExcelWriter(target_excel_path, engine="openpyxl") as writer:
                df_clients.to_excel(writer, sheet_name="Clientes", index=False)
                df_services.to_excel(writer, sheet_name="Servicos", index=False)

            logger.info(f"Exportacao SQLite -> Excel gerada em {target_excel_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao exportar SQLite -> Excel: {e}", exc_info=True)
            return False
