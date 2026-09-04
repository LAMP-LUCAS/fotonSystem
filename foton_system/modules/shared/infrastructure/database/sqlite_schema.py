"""
Definicoes de DDL e inicializacao de tabelas relacionais do SQLite.
"""

import sqlite3

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cod_cliente TEXT,
    alias TEXT NOT NULL UNIQUE,
    nome TEXT,
    status TEXT NOT NULL DEFAULT 'ATIVO',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_clientes_alias ON clientes(alias);
CREATE INDEX IF NOT EXISTS idx_clientes_status ON clientes(status);

CREATE TABLE IF NOT EXISTS servicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cod_servico TEXT,
    cliente_alias TEXT NOT NULL,
    alias TEXT NOT NULL,
    tipo TEXT,
    status TEXT NOT NULL DEFAULT 'ATIVO',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(cliente_alias) REFERENCES clientes(alias) ON DELETE CASCADE,
    UNIQUE(cliente_alias, alias)
);

CREATE INDEX IF NOT EXISTS idx_servicos_cliente ON servicos(cliente_alias);
CREATE INDEX IF NOT EXISTS idx_servicos_status ON servicos(status);

CREATE TABLE IF NOT EXISTS lancamentos_financeiros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_alias TEXT NOT NULL,
    servico_cod TEXT,
    tipo TEXT NOT NULL CHECK(tipo IN ('ENTRADA', 'SAIDA')),
    categoria TEXT NOT NULL DEFAULT 'OUTROS',
    valor REAL NOT NULL CHECK(valor >= 0),
    data_mov TEXT NOT NULL,
    data_vencimento TEXT,
    descricao TEXT NOT NULL,
    conciliado INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(cliente_alias) REFERENCES clientes(alias) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_fin_cliente ON lancamentos_financeiros(cliente_alias);
CREATE INDEX IF NOT EXISTS idx_fin_servico ON lancamentos_financeiros(servico_cod);
CREATE INDEX IF NOT EXISTS idx_fin_data ON lancamentos_financeiros(data_mov);
"""


def init_schema(conn: sqlite3.Connection) -> None:
    """Executa o script de criacao de tabelas e indices de forma transacional."""
    with conn:
        conn.executescript(SCHEMA_SQL)
