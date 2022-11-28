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
        expression = self.expression.transpile().operate(self, check_any = False)
        keyword = self.type_keyword.token.string

        if keyword == "bool":
            return expression.new("%s" if expression.e_type == "bool" else "(%s != 0)").cast("bool")

        type_keyword = self.type_keyword.transpile()
        e_type, c_type = type_keyword.e_type, type_keyword.c_type

        if keyword not in ("imag32", "imag64", "imag"):
            return expression.new(f"({c_type})(%s)").cast(e_type)

        suffix = "f" if keyword == "imag32" else ("l" if keyword == "imag" else "")
        self.transpiler.include("complex")
        return expression.new(f"(cimag{suffix}(%s) * 1.0j)").cast(e_type)
