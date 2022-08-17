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

        match operator.string:
            case "+":
                node_cls = UnaryPlusExpression
            case "-":
                node_cls = UnaryMinusExpression
            case "!":
                node_cls = BitwiseNotExpression
            case "~"|"<~"|"~>":
                node_cls = RoundExpression

        return node_cls(operator, cls.construct())

class UnaryPlusExpression(UnaryExpression):
    def transpile(self):
        e_type, exp = self.expression.transpile()
        if e_type == "i64" and exp.of(PrimaryNode) and exp.token.of("NumericConstant"):
            return ("u64", f"{exp}U")

        return (e_type, exp)

class UnaryMinusExpression(UnaryExpression):
    def transpile(self):
        e_type, expression = self.expression.transpile()
        e_type = "i64" if e_type in ("u64", "bool") else e_type
        e_type = "imax" if e_type == "umax" else e_type
        return (e_type, f"-{expression}")

class BitwiseNotExpression(UnaryExpression):
    def transpile(self):
        e_type, expression = self.expression.transpile()
        e_type = "u64" if e_type == "bool" else e_type

        if e_type not in ("f64", "fmax", "c64", "cmax"):
            return (e_type, f"~{expression}")

        message = f"Cannot perform bitwise operation '{self.operator.string}' on "
        message += "floating type."
        self.transpiler.warnings.error(self, message)
        return (e_type, f"/*!*/{expression}")

class RoundExpression(UnaryExpression):
    wrote = []

    def transpile(self):
        e_type, expression = self.expression.transpile()
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
