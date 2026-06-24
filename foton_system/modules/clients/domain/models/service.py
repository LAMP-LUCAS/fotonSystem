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
    def from_row(cls, row: Dict[str, Any]) -> Optional['Service']:
        codigo = ServiceCode(row["CodServico"]) if row.get("CodServico") else None
        return cls(
            client_alias=row.get("AliasCliente", ""),
            alias=row.get("Alias", ""),
            codigo=codigo,
            modalidade=row.get("Modalidade", ""),
            ano=row.get("Ano", ""),
            demanda=row.get("Demanda", ""),
            area_total=float(row.get("AreaTotal", 0) or 0),
            area_coberta=float(row.get("AreaCoberta", 0) or 0),
            area_descoberta=float(row.get("AreaDescoberta", 0) or 0),
            detalhes=row.get("Detalhes", ""),
            estilo=row.get("Estilo", ""),
            ambientes=row.get("Ambientes", ""),
            valor_proposta=float(row.get("ValorProposta", 0) or 0),
            valor_contrato=float(row.get("ValorContrato", 0) or 0),
            status=row.get("Status", "ATIVO"),
            _id=row.get("ID"),
        )