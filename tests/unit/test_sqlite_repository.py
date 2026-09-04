import unittest
import tempfile
from pathlib import Path
import pandas as pd

from foton_system.modules.shared.infrastructure.database import (
    SQLiteClientRepository,
    SQLiteMigrationService,
    SQLiteConnection,
    init_schema,
)


class TestSQLiteRepository(unittest.TestCase):
    def setUp(self):
        self._temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.db_path = Path(self._temp_dir.name) / "test_foton.db"
        self.repo = SQLiteClientRepository(db_path=self.db_path)

    def tearDown(self):
        self._temp_dir.cleanup()

    def test_schema_criado_com_sucesso(self):
        """Verifica se tabelas e indices foram criados."""
        conn = SQLiteConnection.get_connection(self.db_path)
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row['name'] for row in cur.fetchall()}
        conn.close()

        self.assertIn("clientes", tables)
        self.assertIn("servicos", tables)
        self.assertIn("lancamentos_financeiros", tables)

    def test_crud_clientes_e_soft_delete(self):
        """Salva cliente, consulta, aplica soft delete e restaura."""
        df = pd.DataFrame([
            {"CodCliente": "C001", "Alias": "001_CLIENTE_A", "NomeCliente": "Cliente A", "Status": "ATIVO"},
            {"CodCliente": "C002", "Alias": "002_CLIENTE_B", "NomeCliente": "Cliente B", "Status": "ATIVO"},
        ])
        self.repo.save_clients(df)

        # Consulta ativos
        ativos = self.repo.get_clients_dataframe()
        self.assertEqual(len(ativos), 2)

        # Soft delete
        deleted = self.repo.soft_delete_client("001_CLIENTE_A")
        self.assertTrue(deleted)

        ativos_pos = self.repo.get_clients_dataframe()
        self.assertEqual(len(ativos_pos), 1)
        self.assertEqual(ativos_pos.iloc[0]['Alias'], "002_CLIENTE_B")

        todos = self.repo.get_all_clients_dataframe()
        self.assertEqual(len(todos), 2)

        # Restore
        restored = self.repo.restore_client("001_CLIENTE_A")
        self.assertTrue(restored)
        self.assertEqual(len(self.repo.get_clients_dataframe()), 2)

    def test_crud_servicos_e_soft_delete(self):
        """Salva servico vinculado a cliente, consulta e aplica soft delete."""
        # Cria cliente primeiro
        df_cli = pd.DataFrame([
            {"CodCliente": "C001", "Alias": "CLI_ALPHA", "NomeCliente": "Alpha", "Status": "ATIVO"}
        ])
        self.repo.save_clients(df_cli)

        df_srv = pd.DataFrame([
            {"CodServico": "S01", "AliasCliente": "CLI_ALPHA", "Alias": "SRV_PROJETO", "Tipo": "ARQ", "Status": "ATIVO"}
        ])
        self.repo.save_services(df_srv)

        srvs = self.repo.get_services_dataframe()
        self.assertEqual(len(srvs), 1)
        self.assertEqual(srvs.iloc[0]['Alias'], "SRV_PROJETO")

        # Soft delete do servico
        self.assertTrue(self.repo.soft_delete_service("CLI_ALPHA", "SRV_PROJETO"))
        self.assertEqual(len(self.repo.get_services_dataframe()), 0)
        self.assertEqual(len(self.repo.get_all_services_dataframe()), 1)

        # Restore
        self.assertTrue(self.repo.restore_service("CLI_ALPHA", "SRV_PROJETO"))
        self.assertEqual(len(self.repo.get_services_dataframe()), 1)

    def test_migracao_excel_para_sqlite_e_exportacao(self):
        """Testa migracao de planilha baseDados.xlsx para SQLite e reexportacao."""
        excel_path = Path(self._temp_dir.name) / "baseDados_teste.xlsx"
        df_clients = pd.DataFrame([
            {"CodCliente": "C10", "Alias": "CLIENTE_X", "NomeCliente": "Sr. X", "Status": "ATIVO"},
            {"CodCliente": "C20", "Alias": "CLIENTE_Y", "NomeCliente": "Sra. Y", "Status": "ATIVO"},
        ])
        df_services = pd.DataFrame([
            {"CodServico": "SX1", "AliasCliente": "CLIENTE_X", "Alias": "SRV_CONSULTORIA", "Tipo": "ADM", "Status": "ATIVO"}
        ])

        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            df_clients.to_excel(writer, sheet_name="Clientes", index=False)
            df_services.to_excel(writer, sheet_name="Servicos", index=False)

        # Migra
        res = SQLiteMigrationService.migrate_from_excel(excel_path, self.repo)
        self.assertTrue(res['success'])
        self.assertEqual(res['clients_migrated'], 2)
        self.assertEqual(res['services_migrated'], 1)

        # Verifica dados no SQLite
        cli_sqlite = self.repo.get_clients_dataframe()
        self.assertEqual(len(cli_sqlite), 2)
        srv_sqlite = self.repo.get_services_dataframe()
        self.assertEqual(len(srv_sqlite), 1)

        # Exporta de volta para Excel
        exported_excel = Path(self._temp_dir.name) / "baseDados_exportada.xlsx"
        self.assertTrue(SQLiteMigrationService.export_to_excel(self.repo, exported_excel))
        self.assertTrue(exported_excel.exists())


if __name__ == '__main__':
    unittest.main()
