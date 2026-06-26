import math
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
    def _is_empty(cls, val) -> bool:
        if val is None:
            return True
        if isinstance(val, float) and math.isnan(val):
            return True
        return False

    @classmethod
    def _parse_code(cls, raw) -> Optional['ClientCode']:
        if cls._is_empty(raw):
            return None
        try:
            return ClientCode(raw)
        except ValueError:
            return None

    @classmethod
    def _parse_tax_id(cls, raw) -> Optional['TaxId']:
        if cls._is_empty(raw):
            return None
        try:
            return TaxId(raw)
        except ValueError:
            return None

    @classmethod
    def _safe_str(cls, row, key, default=""):
        val = row.get(key, default)
        if isinstance(val, float) and math.isnan(val):
            return default
        return val if val is not None else default

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> Optional['Client']:
        return cls(
            nome=cls._safe_str(row, "NomeCliente", ""),
            alias=cls._safe_str(row, "Alias", ""),
            codigo=cls._parse_code(row.get("CodCliente")),
            nif=cls._parse_tax_id(row.get("NIF")),
            email=cls._safe_str(row, "Email", ""),
            telefone=cls._safe_str(row, "Telefone", ""),
            endereco=cls._safe_str(row, "Endereco", ""),
            status=cls._safe_str(row, "Status", "ATIVO"),
            _id=row.get("ID"),
        )