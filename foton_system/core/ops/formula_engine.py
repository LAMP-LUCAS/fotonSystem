"""[COMPATIBILIDADE] Re-export de FormulaEngine.

A implementação canônica foi movida para
`foton_system.modules.shared.domain.services.formula_engine` para eliminar o
ciclo de dependência entre core.ops e modules.documents.
"""

from foton_system.modules.shared.domain.services.formula_engine import (
    FormulaEngine,
    FormulaResult,
    _parse_br_value,
    _parse_value_for_eval,
)

__all__ = [
    "FormulaEngine",
    "FormulaResult",
    "_parse_br_value",
    "_parse_value_for_eval",
]
