import unittest
from foton_system.modules.clients.domain.models import Client
from foton_system.modules.clients.domain.value_objects import ClientCode, TaxId

class TestClient(unittest.TestCase):
    def test_create_client_basic(self):
        client = Client(nome="João Silva", alias="JOASILVA")
        self.assertEqual(client.nome, "João Silva")
        self.assertEqual(client.alias, "JOASILVA")
        self.assertEqual(client.status, "ATIVO")
    
    def test_soft_delete(self):
        client = Client(nome="João Silva", alias="JOASILVA")
        client.soft_delete()
        self.assertEqual(client.status, "DELETADO")
        self.assertFalse(client.is_active())
    
    def test_restore(self):
        client = Client(nome="João Silva", alias="JOASILVA")
        client.soft_delete()
        client.restore()
        self.assertEqual(client.status, "ATIVO")
        self.assertTrue(client.is_active())
    
    def test_to_row(self):
        code = ClientCode("JOS01")
        client = Client(
            nome="João Silva",
            alias="JOASILVA",
            codigo=code,
            email="joao@example.com",
            telefone="11999998888",
            status="ATIVO",
            _id=1
        )
        row = client.to_row()
        self.assertEqual(row["NomeCliente"], "João Silva")
        self.assertEqual(row["Alias"], "JOASILVA")
        self.assertEqual(row["CodCliente"], "JOS01")
        self.assertEqual(row["Email"], "joao@example.com")
        self.assertEqual(row["Status"], "ATIVO")
    
    def test_from_row(self):
        row = {
            "ID": 1,
            "NomeCliente": "João Silva",
            "Alias": "JOASILVA",
            "CodCliente": "JOS01",
            "Email": "joao@example.com",
            "Telefone": "11999998888",
            "Endereco": "Rua 1",
            "Status": "ATIVO",
        }
        client = Client.from_row(row)
        self.assertEqual(client.nome, "João Silva")
        self.assertEqual(client.alias, "JOASILVA")
        self.assertEqual(str(client.codigo), "JOS01")
        self.assertTrue(client.is_active())

    def test_from_row_no_code(self):
        row = {
            "ID": 2,
            "NomeCliente": "Maria Souza",
            "Alias": "MARSOUZA",
            "Status": "ATIVO",
        }
        client = Client.from_row(row)
        self.assertEqual(client.nome, "Maria Souza")
        self.assertEqual(client.alias, "MARSOUZA")
        self.assertIsNone(client.codigo)
        self.assertTrue(client.is_active())

if __name__ == "__main__":
    unittest.main()