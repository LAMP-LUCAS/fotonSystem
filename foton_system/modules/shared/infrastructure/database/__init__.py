"""
Pacote de persistencia relacional SQLite para o Foton System.
"""

from foton_system.modules.shared.infrastructure.database.sqlite_connection import SQLiteConnection
from foton_system.modules.shared.infrastructure.database.sqlite_schema import init_schema
from foton_system.modules.shared.infrastructure.database.sqlite_client_repository import SQLiteClientRepository
from foton_system.modules.shared.infrastructure.database.sqlite_migration_service import SQLiteMigrationService

__all__ = [
    "SQLiteConnection",
    "init_schema",
    "SQLiteClientRepository",
    "SQLiteMigrationService",
]
