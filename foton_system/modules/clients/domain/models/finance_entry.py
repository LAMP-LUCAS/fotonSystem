import re
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

_DATA_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CATEGORIAS_SAIDA_VALIDAS = {"MAO_DE_OBRA", "MATERIAL", "TAXA", "IMPOSTO", "OUTROS"}


@dataclass
class FinanceEntry:
    tipo: str
    valor: float
    descricao: str
    data: str
    cliente_alias: str
    categoria: str = "OUTROS"
    data_vencimento: Optional[str] = None
    servico_cod: Optional[str] = None
    conciliado: bool = False
    _id: Optional[int] = field(default=None, repr=False)
    _unvalidated: bool = field(default=False, repr=False, compare=False)

    def __post_init__(self):
        if self._unvalidated:
            return
        tipo_upper = self.tipo.upper()
        if tipo_upper not in ("ENTRADA", "SAIDA"):
            raise ValueError(f"Tipo invalido: {self.tipo}. Use ENTRADA ou SAIDA.")
        if self.valor < 0:
            raise ValueError(f"Valor nao pode ser negativo: {self.valor}")
        if not self.descricao.strip():
            raise ValueError("Descricao nao pode ser vazia.")
        if not _DATA_REGEX.match(self.data):
            raise ValueError(f"Data invalida: {self.data}. Use formato YYYY-MM-DD.")
        if not self.cliente_alias.strip():
            raise ValueError("cliente_alias nao pode ser vazio.")

        # RULE-FINANCEIRO-1.5: categoria obrigatoria para SAIDA com valores validos
        if tipo_upper == "SAIDA":
            cat_upper = (self.categoria or "OUTROS").strip().upper()
            if cat_upper not in CATEGORIAS_SAIDA_VALIDAS:
                raise ValueError(
                    f"Categoria invalida para SAIDA: {self.categoria}. "
                    f"Valores permitidos: {', '.join(sorted(CATEGORIAS_SAIDA_VALIDAS))}"
                )
            self.categoria = cat_upper
        else:
            self.categoria = (self.categoria or "").strip().upper()

        # RULE-FINANCEIRO-1.6: data_vencimento opcional com validacao de formato
        if self.data_vencimento:
            venc = str(self.data_vencimento).strip()
            if venc and not _DATA_REGEX.match(venc):
                raise ValueError(f"Data de vencimento invalida: {venc}. Use formato YYYY-MM-DD.")
            self.data_vencimento = venc if venc else None

        if self.servico_cod:
            self.servico_cod = str(self.servico_cod).strip() or None

    def to_row(self) -> Dict[str, Any]:
        return {
            "ID": self._id,
            "Tipo": self.tipo.upper(),
            "Valor": self.valor,
            "Descricao": self.descricao,
            "Data": self.data,
            "Cliente": self.cliente_alias,
            "Categoria": self.categoria,
            "DataVencimento": self.data_vencimento or "",
            "ServicoCod": self.servico_cod or "",
            "Conciliado": "SIM" if self.conciliado else "NAO",
        }

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> Optional['FinanceEntry']:
        conc_val = str(row.get("Conciliado", "")).strip().upper()
        conciliado = conc_val in ("SIM", "TRUE", "1")
        venc = row.get("DataVencimento") or row.get("data_vencimento") or None
        serv = row.get("ServicoCod") or row.get("servico_cod") or None
        cat = row.get("Categoria") or row.get("categoria") or "OUTROS"

        return cls(
            tipo=row.get("Tipo", ""),
            valor=float(row.get("Valor", 0) or 0),
            descricao=row.get("Descricao", ""),
            data=row.get("Data", ""),
            cliente_alias=row.get("Cliente", ""),
            categoria=str(cat).strip().upper(),
            data_vencimento=str(venc).strip() if venc else None,
            servico_cod=str(serv).strip() if serv else None,
            conciliado=conciliado,
            _id=row.get("ID"),
            _unvalidated=True,
        )
