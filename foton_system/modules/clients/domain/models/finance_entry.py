from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class FinanceEntry:
    tipo: str
    valor: float
    descricao: str
    data: str
    cliente_alias: str
    _id: Optional[int] = field(default=None, repr=False)

    def __post_init__(self):
        if self.tipo.upper() not in ("ENTRADA", "SAIDA"):
            raise ValueError(f"Tipo invalido: {self.tipo}. Use ENTRADA ou SAIDA.")
        if self.valor < 0:
            raise ValueError(f"Valor nao pode ser negativo: {self.valor}")
        if not self.descricao.strip():
            raise ValueError("Descricao nao pode ser vazia.")

    def to_row(self) -> Dict[str, Any]:
        return {
            "ID": self._id,
            "Tipo": self.tipo.upper(),
            "Valor": self.valor,
            "Descricao": self.descricao,
            "Data": self.data,
            "Cliente": self.cliente_alias,
        }

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> Optional['FinanceEntry']:
        return cls(
            tipo=row.get("Tipo", ""),
            valor=float(row.get("Valor", 0) or 0),
            descricao=row.get("Descricao", ""),
            data=row.get("Data", ""),
            cliente_alias=row.get("Cliente", ""),
            _id=row.get("ID"),
        )
