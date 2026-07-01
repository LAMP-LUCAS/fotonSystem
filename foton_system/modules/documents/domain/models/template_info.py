from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TemplateInfo:
    filename: str
    description: str = ""
    category: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    version: Optional[str] = None
