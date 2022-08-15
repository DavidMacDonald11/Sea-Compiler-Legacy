from ..expressions.expression import Expression
from ..node import Node

class ExpressionStatement(Node):
    @property
    def nodes(self) -> list:
        return [self.expression]

    def __init__(self, expression):
        self.expression = expression

    @classmethod
    def construct(cls):
        expression = Expression.construct()
        cls.parser.expecting_has(r"\n", "EOF")
        return cls(expression)

    def transpile(self):
        e_type, expression = self.expression.transpile()
        self.transpiler.write(f"{expression}; /*{e_type}*/")
