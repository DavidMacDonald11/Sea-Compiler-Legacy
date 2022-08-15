from .bitwise_or_expression import BitwiseOrExpression
from ..declarations.type_keyword import TypeKeyword
from ..node import Node

class CastExpression(Node):
    @property
    def nodes(self) -> list:
        return [self.expression, self.type_keyword]

    def __init__(self, expression, type_keyword):
        self.expression = expression
        self.type_keyword = type_keyword

    @classmethod
    def construct(cls):
        expression = BitwiseOrExpression.construct()

        while cls.parser.next.has("as"):
            cls.parser.take()
            expression = cls(expression, TypeKeyword.construct())

        return expression

    def transpile(self):
        e_type, expression = self.expression.transpile()

        if self.type_keyword.token.has("bool"):
            return ("bool", expression if e_type == "bool" else f"({expression}) != 0")

        casted_e_type, keyword = self.type_keyword.transpile()
        sea_keyword =self.type_keyword.token.string

        if sea_keyword not in ("imag32", "imag64", "imag"):
            return (casted_e_type, f"({keyword})({expression})")

        suffix = "f" if sea_keyword == "imag32" else ("l" if sea_keyword == "imag" else "")
        self.transpiler.include("complex")
        return (casted_e_type, f"(cimag{suffix}({expression}) * 1.0j)")
