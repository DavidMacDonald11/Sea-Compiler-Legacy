from lexing.token import PREFIX_UNARY_OPERATORS
from .exponential_expression import ExponentialExpression
from ..node import Node, PrimaryNode

class UnaryExpression(Node):
    @property
    def nodes(self) -> list:
        return [self.operator, self.expression]

    def __init__(self, operator, expression):
        self.operator = operator
        self.expression = expression

    @classmethod
    def construct(cls):
        if not cls.parser.next.has(*PREFIX_UNARY_OPERATORS):
            return ExponentialExpression.construct()

        operator = cls.parser.take()
        return cls(operator, cls.construct())

    def transpile(self, transpiler):
        expression = self.expression.transpile(transpiler)

        if self.operator.has("+"):
            is_signed_int = transpiler.expression_type == "i64"
            is_signed_int = is_signed_int and self.expression.of(PrimaryNode)
            is_signed_int = is_signed_int and self.expression.token.of("NumericConstant")
            is_signed_int = is_signed_int and self.expression.token.specifier == "int"

            if is_signed_int:
                transpiler.expression_type = "u64"

            return expression

        if self.operator.has("-"):
            if transpiler.expression_type == "u64":
                transpiler.expression_type = "i64"

            return f"-{expression}"

        if self.operator.has("!"):
            return f"~{expression}"

        if transpiler.expression_type != "f64":
            return expression

        shift = {
            "~": " + .5",
            "~>": " + 1",
            "<~": ""
        }[self.operator.string]

        return f"((f64)(i64)({expression}{shift}))"
