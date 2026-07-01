import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from foton_system.modules.shared.domain.exceptions import FormulaError
from foton_system.modules.shared.domain.services.safe_math import safe_eval
from foton_system.modules.shared.infrastructure.utils.formatting import FotonFormatter

# @story: STORY-026 @rule: RULE-DOC-4.3 @rule: RULE-DOC-4.4

@dataclass
class FormulaResult:
    var: str
    expression: str
    result: Optional[float]
    status: str  # "OK" or "ERRO"


def _parse_br_value(value: str) -> float:
    if not value or not value.strip():
        return 0.0
    try:
        return float(FotonFormatter.parse_br_number(value))
    except (ValueError, TypeError):
        return 0.0


def _parse_value_for_eval(raw: str) -> float:
    if not raw or not raw.strip():
        return 0.0
    raw = raw.strip()
    is_percent = raw.endswith('%')
    if is_percent:
        raw = raw[:-1]
    try:
        val = float(FotonFormatter.parse_br_number(raw))
    except (ValueError, TypeError):
        val = 0.0
    if is_percent:
        val = val / 100.0
    return val


class FormulaEngine:
    def __init__(self):
        self._results: List[FormulaResult] = []

    def resolve(self, replacements: Dict[str, str]) -> Dict[str, str]:
        self._results = []
        for key in list(replacements.keys()):
            value = replacements.get(key, '')
            if isinstance(value, str) and '[calculo:' in value:
                self._resolve_var(key, replacements, set())
        return replacements

    def evaluate_expression(self, expr: str, var_map: Dict[str, str]) -> float:
        self._results = []
        if not expr or not expr.strip():
            return 0.0
        try:
            safe_expr = expr
            sorted_vars = sorted(var_map.keys(), key=len, reverse=True)
            for var in sorted_vars:
                raw_val = var_map.get(var, '')
                val = _parse_value_for_eval(raw_val)
                clean_key = var.lstrip('@')
                safe_expr = safe_expr.replace(f"@{clean_key}", str(val))
            safe_expr = re.sub(r'[^0-9+\-*/().\s]', '', safe_expr)
            if not safe_expr.strip():
                return 0.0
            result = float(safe_eval(safe_expr))
            self._results.append(FormulaResult(
                var='expression',
                expression=expr,
                result=result,
                status='OK'
            ))
            return result
        except FormulaError:
            self._results.append(FormulaResult(
                var='expression',
                expression=expr,
                result=None,
                status='ERRO'
            ))
            raise
        except (ValueError, TypeError) as e:
            self._results.append(FormulaResult(
                var='expression',
                expression=expr,
                result=None,
                status='ERRO'
            ))
            raise FormulaError(expr, str(e))

    def report(self) -> List[FormulaResult]:
        return list(self._results)

    def _resolve_var(self, key: str, replacements: Dict[str, str], visited: set):
        if key in visited:
            self._results.append(FormulaResult(
                var=key, expression='', result=None, status='ERRO'
            ))
            return

        value = replacements.get(key, '')
        if not isinstance(value, str) or '[calculo:' not in value:
            return

        match = re.search(r'\[calculo:\s*(.+?)\]', value)
        if not match:
            self._results.append(FormulaResult(
                var=key, expression='', result=0.0, status='OK'
            ))
            replacements[key] = '0.00'
            return

        visited = visited | {key}
        expression = match.group(1)

        for k in sorted(replacements.keys(), key=len, reverse=True):
            if k.lower() in expression.lower() and k != key:
                ref_val = replacements[k]
                if isinstance(ref_val, str) and '[calculo:' in ref_val:
                    self._resolve_var(k, replacements, visited.copy())
                    ref_val = replacements[k]
                try:
                    numeric = _parse_br_value(ref_val)
                    expression = re.sub(
                        re.escape(k), str(numeric), expression, flags=re.IGNORECASE
                    )
                except (ValueError, TypeError):
                    expression = re.sub(
                        re.escape(k), '0.0', expression, flags=re.IGNORECASE
                    )

        expression = re.sub(r'@[\w%]+', '0.0', expression)

        if not re.match(r'^[\d\.\-\+\*\/\(\)\s]+$', expression):
            result = 0.0
            replacements[key] = f"{result:.2f}"
            self._results.append(FormulaResult(
                var=key, expression=match.group(1), result=result, status='ERRO'
            ))
            return

        try:
            result = safe_eval(expression)
            replacements[key] = f"{result:.2f}"
            self._results.append(FormulaResult(
                var=key, expression=match.group(1), result=result, status='OK'
            ))
        except FormulaError:
            replacements[key] = '0.00'
            self._results.append(FormulaResult(
                var=key, expression=match.group(1), result=None, status='ERRO'
            ))
