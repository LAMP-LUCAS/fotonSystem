import unittest
from foton_system.modules.clients.domain.models import Service
from foton_system.modules.clients.domain.value_objects import ServiceCode

class TestService(unittest.TestCase):
    def test_create_service_basic(self):
        service = Service(client_alias="JOASILVA", alias="PROJETO")
        self.assertEqual(service.client_alias, "JOASILVA")
        self.assertEqual(service.alias, "PROJETO")
        self.assertEqual(service.status, "ATIVO")
    
    def test_soft_delete(self):
        service = Service(client_alias="JOASILVA", alias="PROJETO")
        service.soft_delete()
        self.assertEqual(service.status, "DELETADO")
        self.assertFalse(service.is_active())
    
    def test_restore(self):
        service = Service(client_alias="JOASILVA", alias="PROJETO")
        service.soft_delete()
        service.restore()
        self.assertEqual(service.status, "ATIVO")
        self.assertTrue(service.is_active())
    
    def test_to_row(self):
        code = ServiceCode("JOSRES01")
        service = Service(
            client_alias="JOASILVA",
            alias="PROJETO",
            codigo=code,
            modalidade="Arquitetura",
            ano="2026",
            status="ATIVO",
            _id=1
        )
        row = service.to_row()
        self.assertEqual(row["AliasCliente"], "JOASILVA")
        self.assertEqual(row["Alias"], "PROJETO")
        self.assertEqual(row["CodServico"], "JOSRES01")
        self.assertEqual(row["Modalidade"], "Arquitetura")
        self.assertEqual(row["Status"], "ATIVO")
    
    def test_from_row(self):
        row = {
            "ID": 1,
            "AliasCliente": "JOASILVA",
            "Alias": "PROJETO",
            "CodServico": "JOSRES01",
            "Modalidade": "Arquitetura",
            "Ano": "2026",
            "Status": "ATIVO",
        }
        service = Service.from_row(row)
        self.assertEqual(service.client_alias, "JOASILVA")
        self.assertEqual(service.alias, "PROJETO")
        self.assertEqual(str(service.codigo), "JOSRES01")
        self.assertTrue(service.is_active())

    def test_from_row_no_code(self):
        row = {
            "ID": 2,
            "AliasCliente": "MARSOUZA",
            "Alias": "REFORMA",
            "Status": "ATIVO",
        }
        service = Service.from_row(row)
        self.assertEqual(service.client_alias, "MARSOUZA")
        self.assertEqual(service.alias, "REFORMA")
        self.assertIsNone(service.codigo)
        self.assertTrue(service.is_active())

if __name__ == "__main__":
    unittest.main()