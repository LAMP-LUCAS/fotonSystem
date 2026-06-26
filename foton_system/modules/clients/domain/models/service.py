import math
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from foton_system.modules.clients.domain.value_objects import ServiceCode

@dataclass
class Service:
    client_alias: str
    alias: str
    codigo: Optional[ServiceCode] = None
    modalidade: str = ""
    ano: str = ""
    demanda: str = ""
    area_total: float = 0.0
    area_coberta: float = 0.0
    area_descoberta: float = 0.0
    detalhes: str = ""
    estilo: str = ""
    ambientes: str = ""
    valor_proposta: float = 0.0
    valor_contrato: float = 0.0
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
            "AliasCliente": self.client_alias,
            "Alias": self.alias,
            "CodServico": str(self.codigo) if self.codigo else None,
            "Modalidade": self.modalidade,
            "Ano": self.ano,
            "Demanda": self.demanda,
            "AreaTotal": self.area_total,
            "AreaCoberta": self.area_coberta,
            "AreaDescoberta": self.area_descoberta,
            "Detalhes": self.detalhes,
            "Estilo": self.estilo,
            "Ambientes": self.ambientes,
            "ValorProposta": self.valor_proposta,
            "ValorContrato": self.valor_contrato,
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
    def _parse_code(cls, raw) -> Optional['ServiceCode']:
        if cls._is_empty(raw):
            return None
        try:
            return ServiceCode(raw)
        except ValueError:
            return None

    @classmethod
    def _safe_str(cls, row, key, default=""):
        val = row.get(key, default)
        if isinstance(val, float) and math.isnan(val):
            return default
        return val if val is not None else default

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> Optional['Service']:
        return cls(
            client_alias=cls._safe_str(row, "AliasCliente", ""),
            alias=cls._safe_str(row, "Alias", ""),
            codigo=cls._parse_code(row.get("CodServico")),
            modalidade=cls._safe_str(row, "Modalidade", ""),
            ano=cls._safe_str(row, "Ano", ""),
            demanda=cls._safe_str(row, "Demanda", ""),
            area_total=float(row.get("AreaTotal", 0) or 0),
            area_coberta=float(row.get("AreaCoberta", 0) or 0),
            area_descoberta=float(row.get("AreaDescoberta", 0) or 0),
            detalhes=cls._safe_str(row, "Detalhes", ""),
            estilo=cls._safe_str(row, "Estilo", ""),
            ambientes=cls._safe_str(row, "Ambientes", ""),
            valor_proposta=float(row.get("ValorProposta", 0) or 0),
            valor_contrato=float(row.get("ValorContrato", 0) or 0),
            status=cls._safe_str(row, "Status", "ATIVO"),
            _id=row.get("ID"),
        )