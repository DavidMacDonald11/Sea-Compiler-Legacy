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

    def transpile(self):
        e_type, expression = self.expression.transpile()

        if self.operator.has("%"):
            return self.transpile_percent(e_type, expression)

        if self.operator.has("?"):
            return self.transpile_test(e_type, expression)

        return self.transpile_factorial(e_type, expression)

    def transpile_percent(self, e_type, expression):
        e_type = "u64" if e_type == "bool" else e_type
        return (e_type, f"({expression} / 100)")

    def transpile_test(self, e_type, expression):
        return ("bool", expression if e_type == "bool" else f"({expression} != 0)")

    def transpile_factorial(self, e_type, expression):
        if e_type in ("f64", "fmax", "c64", "cmax"):
            self.transpiler.warnings.error(self, "Cannot use factorial on floats")
            return (e_type, f"({expression}/*!*/)")

        func = self.write_factorial_func()
        return ("u64", f"({func}({expression}))")

    def write_factorial_func(self):
        func = "__sea_func_factorial__"

        if type(self).wrote_factorial_func:return func
        type(self).wrote_factorial_func = True

        e_type = self.transpiler.safe_type("u64")

        self.transpiler.header("\n".join((
            f"{e_type} {func}({e_type} num)", "{",
            f"\t{e_type} result = 1;",
            f"\tfor({e_type} i = 2; i <= num; i++) result *= i;",
            "\treturn result;", "}\n"
        )))

        return func
