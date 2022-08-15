from lexing.token import PREFIX_UNARY_OPERATORS
from .exponential_expression import ExponentialExpression
from ..node import Node, PrimaryNode

class UnaryExpression(Node):
    wrote = []

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

    def transpile(self):
        e_type, expression = self.expression.transpile()

        if self.operator.has("+"):
            return self.transpile_plus(e_type, expression)

        if self.operator.has("-"):
            return self.transpile_minus(e_type, expression)

        if self.operator.has("!"):
            return self.transpile_not(e_type, expression)

        return self.transpile_round(e_type, expression)

    def transpile_plus(self, e_type, expression):
        exp = self.expression

        if e_type == "i64" and exp.of(PrimaryNode) and exp.token.of("NumericConstant"):
            return ("u64", f"{expression}U")

        return expression

    def transpile_minus(self, e_type, expression):
        e_type = "i64" if e_type in ("u64", "bool") else e_type
        e_type = "imax" if e_type == "umax" else e_type
        return (e_type, f"-{expression}")

    def transpile_not(self, e_type, expression):
        e_type = "u64" if e_type == "bool" else e_type

        if e_type not in ("f64", "fmax", "c64", "cmax"):
            return (e_type, f"~{expression}")

        message = f"Cannot perform bitwise operation '{self.operator.string}' on "
        message += "floating type."
        self.transpiler.warnings.error(self, message)
        return (e_type, f"/*!*/{expression}")

    def transpile_round(self, e_type, expression):
        e_type = "u64" if e_type == "bool" else e_type

        if e_type in ("u64", "umax", "i64", "imax"):
            return (e_type, expression)

        self.transpiler.include("math")

        if e_type in ("f64", "c64", "cmax"):
            func = {"~": "round", "~>": "ceil", "<~": "floor"}[self.operator.string]
        else:
            func = {"~": "roundl", "~>": "ceill", "<~": "floorl"}[self.operator.string]

        if e_type in ("c64", "cmax"):
            self.transpiler.include("complex")
            func = type(self).write_round_func(self.transpiler, func, e_type)

        return (e_type, f"({func}({expression}))")

    @classmethod
    def write_round_func(cls, transpiler, func, e_type):
        sea_func = f"__sea_func_{func}_{e_type}__"

        if sea_func in cls.wrote: return sea_func
        cls.wrote += [sea_func]

        long = "l" if e_type == "cmax" else ""
        num_re = f"creal{long}(num)"
        num_im = f"cimag{long}(num)"

        e_type = transpiler.safe_type(e_type)

        transpiler.header("\n".join((
            f"{e_type} {sea_func}({e_type} num)", "{",
            f"\treturn {func}{long}({num_re}) + {func}{long}({num_im}) * 1.0j;", "}\n"
        )))

        return sea_func
