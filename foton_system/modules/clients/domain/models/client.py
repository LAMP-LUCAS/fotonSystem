from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from foton_system.modules.clients.domain.value_objects import ClientCode, TaxId

@dataclass
class Client:
    nome: str
    alias: str
    codigo: Optional[ClientCode] = None
    nif: Optional[TaxId] = None
    email: str = ""
    telefone: str = ""
    endereco: str = ""
    status: str = "ATIVO"
    _id: Optional[int] = field(default=None, repr=False)
    
    def soft_delete(self) -> None:
        self.status = "DELETADO"
    
    def restore(self) -> None:
        self.status = "ATIVO"
    
    def is_active(self) -> bool:
        return self.status == "ATIVO"
    
    def to_row(self) -> Dict[str, Any]:
        return {
            "ID": self._id,
            "CodCliente": str(self.codigo) if self.codigo else None,
            "NomeCliente": self.nome,
            "Alias": self.alias,
            "NIF": str(self.nif) if self.nif else "",
            "Email": self.email,
            "Telefone": self.telefone,
            "Endereco": self.endereco,
            "Status": self.status,
        }
    
    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> Optional['Client']:
        codigo = ClientCode(row["CodCliente"]) if row.get("CodCliente") else None
        nif = TaxId(row["NIF"]) if row.get("NIF") else None
        return cls(
            nome=row.get("NomeCliente", ""),
            alias=row.get("Alias", ""),
            codigo=codigo,
            nif=nif,
            email=row.get("Email", ""),
            telefone=row.get("Telefone", ""),
            endereco=row.get("Endereco", ""),
            status=row.get("Status", "ATIVO"),
            _id=row.get("ID"),
        )