"""
FormSession Domain Model - Gerencia o estado e lógica do formulário MD.
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Any

@dataclass
class FormField:
    name: str
    description: str
    original_value: str = "" # Valor exato que veio do MD
    current_value: str = ""  # Valor atual (pode ser editado)
    is_calculated: bool = False
    formula: str = ""
    is_dirty: bool = False
    hint: str = ""

class FormSession:
    def __init__(self) -> None:
        self.fields: List[FormField] = []
        self.cursor: int = 0
        self.structure: List[Dict[str, Any]] = []
        self.var_pattern: re.Pattern = re.compile(r'^@([\w%]+);\s*(.*)$')
        self.calc_pattern: re.Pattern = re.compile(r'^\[calculo:\s*(.*?)\]\s*(.*)$')
        self.hint_pattern: re.Pattern = re.compile(r'(?:por exemplo|exemplo)\s*:?\s*(.+)$', re.IGNORECASE)

    def parse_markdown(self, md_text: str) -> None:
        self.fields = []
        self.structure = []
        lines = md_text.splitlines()
        
        for line in lines:
            stripped = line.strip()
            match = self.var_pattern.match(stripped)
            if match:
                var_name = match.group(1)
                full_content = match.group(2).strip()
                
                if self.calc_pattern.match(full_content):
                    calc_match = self.calc_pattern.match(full_content)
                    f = FormField(
                        name=var_name, 
                        description=calc_match.group(2).strip(),
                        is_calculated=True,
                        formula=calc_match.group(1).strip(),
                        original_value=full_content
                    )
                else:
                    hint = ""
                    hint_match = self.hint_pattern.search(full_content)
                    clean_val = full_content
                    if hint_match:
                        hint = hint_match.group(0).strip()
                        clean_val = self.hint_pattern.sub('', full_content).strip().rstrip(',').rstrip(';')
                    
                    f = FormField(
                        name=var_name, 
                        description=clean_val, 
                        current_value=clean_val,
                        original_value=full_content,
                        hint=hint
                    )
                
                self.fields.append(f)
                self.structure.append({"type": "variable", "name": var_name})
            else:
                self.structure.append({"type": "text", "content": line})
        
        self.cursor = 0
        self.recalculate_all()

    def update_current(self, value: str) -> None:
        if not value.strip(): return
        f = self.get_current_field()
        if f and not f.is_calculated:
            f.current_value = value
            f.is_dirty = True
            self.recalculate_all()

    def get_current_field(self) -> Optional[FormField]:
        return self.fields[self.cursor] if self.fields else None

    def next(self) -> None:
        if self.cursor < len(self.fields) - 1: self.cursor += 1

    def prev(self) -> None:
        if self.cursor > 0: self.cursor -= 1

    def recalculate_all(self) -> None:
        var_map = {f.name: f.current_value for f in self.fields}
        for f in self.fields:
            if f.is_calculated:
                res = self._evaluate(f.formula, var_map)
                f.current_value = f"{res:.2f}"
                if f.name.endswith('%'): f.current_value = f"{res*100:.2f}%"
                var_map[f.name] = f.current_value

    def generate_markdown(self) -> str:
        field_dict = {f.name: f for f in self.fields}
        output = []
        for item in self.structure:
            if item["type"] == "text": 
                output.append(item["content"])
            else:
                f = field_dict[item["name"]]
                val = f"@{f.name};"
                if f.is_calculated:
                    val += f"[calculo: {f.formula}] {f.description}"
                else:
                    if f.is_dirty:
                        val += f.current_value
                        if f.hint: val += f" {f.hint}"
                    else:
                        val += f.original_value
                output.append(val)
        return "\n".join(output)

    def _evaluate(self, expr: str, var_map: Dict[str, str]) -> float:
        try:
            safe_expr = expr
            sorted_vars = sorted(var_map.keys(), key=len, reverse=True)
            for var in sorted_vars:
                raw_val = var_map[var].replace('%', '').replace(',', '.')
                try: val = float(raw_val) if raw_val.strip() else 0.0
                except: val = 0.0
                safe_expr = safe_expr.replace(f"@{var}", str(val))
            safe_expr = re.sub(r'[^0-9+\-*/().\s]', '', safe_expr)
            return float(eval(safe_expr, {"__builtins__": {}}, {})) if safe_expr.strip() else 0.0
        except: return 0.0
