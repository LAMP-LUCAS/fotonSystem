from dataclasses import dataclass
import re

_SERVICE_CODE_PATTERN = re.compile(r'^[A-Z]{6}[0-9]{2}$')

@dataclass(frozen=True)
class ServiceCode:
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Código do serviço não pode ser vazio")
        upper_value = self.value.upper()
        if not _SERVICE_CODE_PATTERN.match(upper_value):
            raise ValueError(f"Código inválido: {self.value}. Formato esperado: XXXXXX## (ex: JOSRES01)")
        object.__setattr__(self, 'value', upper_value)
    
    def __str__(self) -> str:
        return self.value