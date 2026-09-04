"""
Gerenciamento de conexao com SQLite nativo (sqlite3).
Aplica modo WAL e foreign keys ativas para suporte a transacoes ACID concorrentes.
"""

import sqlite3
from pathlib import Path
from typing import Optional


class SQLiteConnection:
    @staticmethod
    def get_connection(db_path: Path, timeout: float = 10.0) -> sqlite3.Connection:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path), timeout=timeout)
        conn.row_factory = sqlite3.Row
        with conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA journal_mode = WAL;")
        return conn
