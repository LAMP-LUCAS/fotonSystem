from dataclasses import dataclass
import re

_PATTERN = re.compile(r'^[\d\.]+$')

@dataclass(frozen=True)
class TaxId:
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("NIF/CPF/CNPJ não pode ser vazio")
        clean = re.sub(r'[^\d]', '', self.value)
        if not (8 <= len(clean) <= 14):
            raise ValueError(f"NIF/CPF/CNPJ inválido: {self.value}. Deve ter 8 a 14 dígitos")
    
    @property
    def clean(self) -> str:
        return re.sub(r'[^\d]', '', self.value)
    
    def __str__(self) -> str:
        return self.value