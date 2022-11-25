from lexing.token import PREFIX_UNARY_OPERATORS
from transpiling.symbols.invariable import Invariable
from .primary_expression import Identifier
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
            case "&"|"$":
                node_cls = OwnershipExpression

        return node_cls(operator, cls.construct())

class UnaryPlusExpression(UnaryExpression):
    def transpile(self):
        exp = self.expression
        expression = exp.transpile().operate()

        if expression.e_type == "i64" and exp.of(PrimaryNode) and exp.token.of("NumericConstant"):
            return expression.new("%sU").cast("u64")

        return expression

class UnaryMinusExpression(UnaryExpression):
    def transpile(self):
        expression = self.expression.transpile().operate(self)

        if expression.e_type in ("u64", "bool"):
            expression.cast("i64")
        elif expression.e_type == "umax":
            expression.cast("imax")

        return expression.new("-%s")

class BitwiseNotExpression(UnaryExpression):
    def transpile(self):
        expression = self.expression.transpile().operate(self).cast_up()

        if expression.e_type not in ("f64", "fmax", "g64", "gmax", "c64", "cmax"):
            return expression.new("~%s")

        message = "Cannot perform bitwise operation on floating type"
        self.transpiler.warnings.error(self, message)
        return expression.new("/*!*/%s")

class RoundExpression(UnaryExpression):
    wrote = []

    def transpile(self):
        expression = self.expression.transpile().operate(self).cast_up()

        if expression.e_type in ("u64", "umax", "i64", "imax"):
            return expression

        self.transpiler.include("math")
        func = {"~": "round", "~>": "ceil", "<~": "floor"}[self.operator.string]

        if expression.e_type not in ("f64", "g64", "gmax", "c64", "cmax"):
            func += "l"

        if expression.e_type in ("g64", "gmax", "c64", "cmax"):
            self.transpiler.include("complex")
            func = type(self).write_func(self.transpiler, func, expression)

        return expression.new(f"({func}(%s))")

    @classmethod
    def write_func(cls, transpiler, func, expression):
        sea_func = f"__sea_func_{func}_{expression.e_type}__"

        if sea_func in cls.wrote: return sea_func
        cls.wrote += [sea_func]

        e_type, c_type = expression.e_type, expression.c_type

        long = "l" if e_type in ("gmax", "cmax") else ""
        real_comp = "" if e_type in ("g64", "gmax") else f"{func}{long}(creal{long}(num)) + "

        transpiler.header("\n".join((
            f"{c_type} {sea_func}({c_type} num)", "{",
            f"\treturn {real_comp}{func}{long}(cimag{long}(num)) * 1.0j;", "}\n"
        )))

        return sea_func

class OwnershipExpression(UnaryExpression):
    def transpile(self):
        self.transpiler.context.in_ownership = True

        operator = self.operator.string
        expression = self.expression.transpile()
        expression.ownership = operator

        if not isinstance(self.expression, Identifier):
            message = "Cannot borrow/transfer ownership of non-identifier"
            self.transpiler.warnings.error(self, message)
            return expression.new(f"/*{operator}*/%s")

        name = self.expression.token.string
        identifier = self.transpiler.symbols.at(self, name)

        if identifier is None:
            return expression.new("/*%s*/")

        expression.is_invar = isinstance(identifier, Invariable)
        expression.owners[0] = identifier
        identifier.is_transfered = operator == "$"

        self.transpiler.context.in_ownership = False
        return expression.new("&%s")
