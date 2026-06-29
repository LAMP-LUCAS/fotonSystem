import re
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

_DATA_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")

@dataclass
class FinanceEntry:
    tipo: str
    valor: float
    descricao: str
    data: str
    cliente_alias: str
    _id: Optional[int] = field(default=None, repr=False)
    _unvalidated: bool = field(default=False, repr=False, compare=False)

    def __post_init__(self):
        if self._unvalidated:
            return
        if self.tipo.upper() not in ("ENTRADA", "SAIDA"):
            raise ValueError(f"Tipo invalido: {self.tipo}. Use ENTRADA ou SAIDA.")
        if self.valor < 0:
            raise ValueError(f"Valor nao pode ser negativo: {self.valor}")
        if not self.descricao.strip():
            raise ValueError("Descricao nao pode ser vazia.")
        if not _DATA_REGEX.match(self.data):
            raise ValueError(f"Data invalida: {self.data}. Use formato YYYY-MM-DD.")
        if not self.cliente_alias.strip():
            raise ValueError("cliente_alias nao pode ser vazio.")

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
            _unvalidated=True,
        )
