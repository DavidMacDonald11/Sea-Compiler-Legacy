from lexing.token import PREFIX_UNARY_OPERATORS
from transpiling.utils import util, new_util
from .primary_expression import Identifier, NumericConstant
from .exponential_expression import ExponentialExpression
from ..node import Node

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
        expression = self.expression.transpile().operate(self)

        if "int" in expression.kind and self.expression.of(NumericConstant):
            return expression.new("%sU").cast_replace("int", "nat")

        return expression

class UnaryMinusExpression(UnaryExpression):
    def transpile(self):
        expression = self.expression.transpile().operate(self).cast_up()

        if "nat" in expression.kind:
            expression.cast_replace("nat", "int")

        return expression.add("-")

class BitwiseNotExpression(UnaryExpression):
    def transpile(self):
        return self.expression.transpile().operate(self).cast_up().add("~")

class RoundExpression(UnaryExpression):
    def transpile(self):
        expression = self.expression.transpile().operate(self).cast_up()
        kind = expression.kind

        if "nat" in kind or "int" in kind:
            return expression

        self.transpiler.include("math")
        func = {"~": "round", "~>": "ceil", "<~": "floor"}[self.operator.string]

        if kind == "real":
            func += "l"

        if "imag" in kind or "cplex" in kind:
            self.transpiler.include("complex")
            func = util(self.util_round(func, kind))

        return expression.add(f"({func}(", "))")

    @staticmethod
    def util_round(s_func, kind):
        name = f"{s_func}_{kind}"

        @new_util(name)
        def func(func):
            long = "l" if kind in ("imag", "cplex") else ""
            real_comp = "" if "imag" in kind else f"{s_func}{long}(creal{long}(num)) + "
            kind = f"__sea_type_{kind}__"

            return "\n".join((
                f"{kind} {func}({kind} num)", "{",
                f"\treturn {real_comp}{s_func}{long}(cimag{long}(num)) * 1.0j;", "}\n"
            ))

        return name

class OwnershipExpression(UnaryExpression):
    def transpile(self):
        self.transpiler.context.in_ownership = True
        expression = self.expression.transpile()

        if not isinstance(self.expression, Identifier):
            message = "Cannot borrow/transfer ownership of non-identifier"
            self.transpiler.warnings.error(self, message)
            return expression

        name = self.expression.token.string
        identifier = self.transpiler.symbols.at(self, name)

        self.transpiler.context.in_ownership = False
        return identifier.transfer(expression, self.operator.string)
