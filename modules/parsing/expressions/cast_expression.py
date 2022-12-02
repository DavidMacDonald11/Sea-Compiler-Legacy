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
        expression = self.expression.transpile().operate(self)
        keyword = self.type_keyword.token.string

        if keyword == "bool":
            if expression.kind == "bool": return expression
            return expression.add("(", " != 0)").cast("bool")

        type_keyword = self.type_keyword.transpile()
        kind = type_keyword.kind

        if "imag" not in keyword:
            return expression.add(f"(__sea_type_{kind}__)(", ")").cast(kind)

        suffix = "f" if "32" in keyword else ("" if "64" in keyword else "l")
        self.transpiler.include("complex")
        return expression.add(f"(cimag{suffix}(", ") * 1.0j)").cast(kind)
