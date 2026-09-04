"""
Implementacao de ClientRepositoryPort baseada em SQLite Relacional.
Garante transacoes ACID, eliminando concorrencia e corrupcao de arquivos Excel.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any, Set
import pandas as pd
import sqlite3

from foton_system.modules.clients.application.ports.client_repository_port import ClientRepositoryPort
from foton_system.modules.clients.domain.models import Client, Service
from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.shared.infrastructure.database.sqlite_connection import SQLiteConnection
from foton_system.modules.shared.infrastructure.database.sqlite_schema import init_schema


class SQLiteClientRepository(ClientRepositoryPort):
    def __init__(self, db_path: Optional[Path] = None, config: Optional[Config] = None):
        self._config = config or Config()
        if db_path is None:
            db_dir = self._config.workspace_path / "data"
            self.db_path = db_dir / "foton_system.db"
        else:
            self.db_path = Path(db_path)

        # Inicializa o schema
        conn = self._get_conn()
        try:
            init_schema(conn)
        finally:
            conn.close()

    def _get_conn(self) -> sqlite3.Connection:
        return SQLiteConnection.get_connection(self.db_path)

    # ================= DataFrames =================

    def get_clients_dataframe(self) -> pd.DataFrame:
        conn = self._get_conn()
        try:
            query = """
                SELECT cod_cliente AS CodCliente, alias AS Alias, nome AS NomeCliente, status AS Status
                FROM clientes
                WHERE status != 'DELETADO'
                ORDER BY alias
            """
            df = pd.read_sql_query(query, conn)
            return df
        finally:
            conn.close()

    def get_all_clients_dataframe(self) -> pd.DataFrame:
        conn = self._get_conn()
        try:
            query = """
                SELECT cod_cliente AS CodCliente, alias AS Alias, nome AS NomeCliente, status AS Status
                FROM clientes
                ORDER BY alias
            """
            return pd.read_sql_query(query, conn)
        finally:
            conn.close()

    def get_services_dataframe(self) -> pd.DataFrame:
        conn = self._get_conn()
        try:
            query = """
                SELECT cod_servico AS CodServico, cliente_alias AS AliasCliente, alias AS Alias, tipo AS Tipo, status AS Status
                FROM servicos
                WHERE status != 'DELETADO'
                ORDER BY cliente_alias, alias
            """
            return pd.read_sql_query(query, conn)
        finally:
            conn.close()

    def get_all_services_dataframe(self) -> pd.DataFrame:
        conn = self._get_conn()
        try:
            query = """
                SELECT cod_servico AS CodServico, cliente_alias AS AliasCliente, alias AS Alias, tipo AS Tipo, status AS Status
                FROM servicos
                ORDER BY cliente_alias, alias
            """
            return pd.read_sql_query(query, conn)
        finally:
            conn.close()

    # ================= Save / Persistencia ACID =================

    def save_clients(self, df: pd.DataFrame) -> None:
        if df is None or df.empty:
            return

        conn = self._get_conn()
        try:
            with conn:
                for _, row in df.iterrows():
                    alias = str(row.get('Alias', '')).strip()
                    if not alias:
                        continue
                    cod = row.get('CodCliente')
                    cod_val = str(cod).strip() if pd.notna(cod) and str(cod).strip() != "" else None
                    nome = row.get('NomeCliente')
                    nome_val = str(nome).strip() if pd.notna(nome) else None
                    status = str(row.get('Status', 'ATIVO')).strip().upper()

                    conn.execute(
                        """
                        INSERT INTO clientes (cod_cliente, alias, nome, status, updated_at)
                        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT(alias) DO UPDATE SET
                            cod_cliente = COALESCE(excluded.cod_cliente, clientes.cod_cliente),
                            nome = COALESCE(excluded.nome, clientes.nome),
                            status = excluded.status,
                            updated_at = CURRENT_TIMESTAMP
                        """,
                        (cod_val, alias, nome_val, status),
                    )
        finally:
            conn.close()

    def save_services(self, df: pd.DataFrame) -> None:
        if df is None or df.empty:
            return

        conn = self._get_conn()
        try:
            with conn:
                for _, row in df.iterrows():
                    cli_alias = str(row.get('AliasCliente', '')).strip()
                    srv_alias = str(row.get('Alias', '')).strip()
                    if not cli_alias or not srv_alias:
                        continue

                    # Garante cliente existente
                    conn.execute(
                        "INSERT OR IGNORE INTO clientes (alias, status) VALUES (?, 'ATIVO')",
                        (cli_alias,),
                    )

                    cod = row.get('CodServico')
                    cod_val = str(cod).strip() if pd.notna(cod) and str(cod).strip() != "" else None
                    tipo = row.get('Tipo')
                    tipo_val = str(tipo).strip() if pd.notna(tipo) else None
                    status = str(row.get('Status', 'ATIVO')).strip().upper()

                    conn.execute(
                        """
                        INSERT INTO servicos (cod_servico, cliente_alias, alias, tipo, status, updated_at)
                        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT(cliente_alias, alias) DO UPDATE SET
                            cod_servico = COALESCE(excluded.cod_servico, servicos.cod_servico),
                            tipo = COALESCE(excluded.tipo, servicos.tipo),
                            status = excluded.status,
                            updated_at = CURRENT_TIMESTAMP
                        """,
                        (cod_val, cli_alias, srv_alias, tipo_val, status),
                    )
        finally:
            conn.close()

    # ================= Soft Delete & Restore =================

    def soft_delete_client(self, alias: str) -> bool:
        conn = self._get_conn()
        try:
            with conn:
                cur = conn.execute(
                    "UPDATE clientes SET status = 'DELETADO', updated_at = CURRENT_TIMESTAMP WHERE alias = ?",
                    (alias,),
                )
                return cur.rowcount > 0
        finally:
            conn.close()

    def restore_client(self, alias: str) -> bool:
        conn = self._get_conn()
        try:
            with conn:
                cur = conn.execute(
                    "UPDATE clientes SET status = 'ATIVO', updated_at = CURRENT_TIMESTAMP WHERE alias = ?",
                    (alias,),
                )
                return cur.rowcount > 0
        finally:
            conn.close()

    def soft_delete_service(self, client_alias: str, service_alias: str) -> bool:
        conn = self._get_conn()
        try:
            with conn:
                cur = conn.execute(
                    "UPDATE servicos SET status = 'DELETADO', updated_at = CURRENT_TIMESTAMP WHERE cliente_alias = ? AND alias = ?",
                    (client_alias, service_alias),
                )
                return cur.rowcount > 0
        finally:
            conn.close()

    def restore_service(self, client_alias: str, service_alias: str) -> bool:
        conn = self._get_conn()
        try:
            with conn:
                cur = conn.execute(
                    "UPDATE servicos SET status = 'ATIVO', updated_at = CURRENT_TIMESTAMP WHERE cliente_alias = ? AND alias = ?",
                    (client_alias, service_alias),
                )
                return cur.rowcount > 0
        finally:
            conn.close()

    def get_deleted_clients(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            cur = conn.execute("SELECT alias, nome, cod_cliente FROM clientes WHERE status = 'DELETADO'")
            return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()

    def get_deleted_services(self) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            cur = conn.execute("SELECT cliente_alias, alias, cod_servico, tipo FROM servicos WHERE status = 'DELETADO'")
            return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()

    # ================= Entity Lists =================

    def get_clients(self) -> List[Client]:
        df = self.get_clients_dataframe()
        return [Client.from_row(row) for _, row in df.iterrows()]

    def get_all_clients(self) -> List[Client]:
        df = self.get_all_clients_dataframe()
        return [Client.from_row(row) for _, row in df.iterrows()]

    def get_services(self) -> List[Service]:
        df = self.get_services_dataframe()
        return [Service.from_row(row) for _, row in df.iterrows()]

    def get_all_services(self) -> List[Service]:
        df = self.get_all_services_dataframe()
        return [Service.from_row(row) for _, row in df.iterrows()]

    # ================= File System Folders =================

    def list_client_folders(self) -> Set[str]:
        base = self._config.base_pasta_clientes
        if not base.exists():
            return set()
        ignored = set(self._config.ignored_folders)
        return {
            p.name for p in base.iterdir()
            if p.is_dir() and not p.name.startswith(('.', '_')) and p.name not in ignored
        }

    def list_service_folders(self, client_name: str) -> Set[str]:
        base = self._config.base_pasta_clientes / client_name
        if not base.exists():
            return set()
        ignored = set(self._config.ignored_folders)
        return {
            p.name for p in base.iterdir()
            if p.is_dir() and not p.name.startswith(('.', '_')) and p.name not in ignored
        }

    def create_folder(self, path: str) -> None:
        Path(path).mkdir(parents=True, exist_ok=True)
