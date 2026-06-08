import ast
import operator

_MAX_TOKENS = 50

_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


class _SafeVisitor(ast.NodeVisitor):
    def __init__(self):
        self._depth = 0

    def visit_Expression(self, node):
        self._depth = 0
        return self.visit(node.body)

    def visit_Constant(self, node):
        if not isinstance(node.value, (int, float)):
            raise ValueError("Valor não numérico")
        return float(node.value)

    def visit_UnaryOp(self, node):
        self._depth += 1
        if self._depth > _MAX_TOKENS:
            raise ValueError("Expressão muito longa")
        op = _ALLOWED_OPS.get(type(node.op))
        if op is None:
            raise ValueError("Operador não permitido")
        operand = self.visit(node.operand)
        return op(operand)

    def visit_BinOp(self, node):
        self._depth += 1
        if self._depth > _MAX_TOKENS:
            raise ValueError("Expressão muito longa")
        op = _ALLOWED_OPS.get(type(node.op))
        if op is None:
            raise ValueError("Operador não permitido")
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Div) and right == 0:
            return 0.0
        return op(left, right)

    def visit_Name(self, node):
        raise ValueError(f"Nome não permitido: {node.id}")

    def visit_Call(self, node):
        raise ValueError("Funções não permitidas")

    def visit_Attribute(self, node):
        raise ValueError("Atributos não permitidos")

    def visit_Subscript(self, node):
        raise ValueError("Subscrição não permitida")

    def generic_visit(self, node):
        if isinstance(node, ast.Expression):
            return super().generic_visit(node)
        raise ValueError(f"Construto não permitido: {type(node).__name__}")


def safe_eval(expression: str) -> float:
    if not expression or not expression.strip():
        return 0.0

    expression = expression.strip()

    if len(expression) > _MAX_TOKENS * 3:
        raise ValueError("Expressão muito longa")

    try:
        tree = ast.parse(expression, mode='eval')
    except SyntaxError:
        raise ValueError("Expressão inválida")

    visitor = _SafeVisitor()
    return float(visitor.visit(tree))
