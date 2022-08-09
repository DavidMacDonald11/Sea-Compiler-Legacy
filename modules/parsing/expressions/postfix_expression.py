from lexing.token import POSTFIX_UNARY_OPERATORS
from .primary_expression import PrimaryExpression
from ..node import Node

class PostfixExpression(Node):
    wrote_factorial_func = False

    @property
    def nodes(self) -> list:
        return [self.expression, self.operator]

    def __init__(self, expression, operator):
        self.expression = expression
        self.operator = operator

    @classmethod
    def construct(cls):
        node = PrimaryExpression.construct()

        if not cls.parser.next.has(*POSTFIX_UNARY_OPERATORS):
            return node

        while cls.parser.next.has(*POSTFIX_UNARY_OPERATORS):
            node = cls(node, cls.parser.take())

        return node

    def transpile(self, transpiler):
        expression = self.expression.transpile(transpiler)

        if self.operator.has("%"):
            return f"({expression} / 100)"

        if transpiler.expression_type == "f64":
            transpiler.warnings.error(self, "Cannot use factorial on floats")
            return f"({expression}/*!*/)"

        transpiler.expression_type = "u64"
        func = type(self).write_factorial_func(transpiler)
        return f"({func}({expression}))"

    @classmethod
    def write_factorial_func(cls, transpiler):
        func = "__sea_func_factorial__"

        if cls.wrote_factorial_func:
            return func

        cls.wrote_factorial_func = True

        transpiler.write("\n".join((
            f"\nu64 {func}(u64 num)", "{",
            "\tu64 result = 1;",
            "\tfor(u64 i = 2; i < result; i++) result *= i;",
            "\treturn result;", "}\n"
        )))

        return func
