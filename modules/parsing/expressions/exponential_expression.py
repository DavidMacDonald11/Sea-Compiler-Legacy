from .postfix_expression import PostfixExpression
from ..node import BinaryOperation

class ExponentialExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["^"], PostfixExpression, cls.parser.unary_expression)

    def transpile(self):
        left = self.left.transpile().operate(self)
        right = self.right.transpile().operate(self)
        result = self.transpiler.expression.resolve(left, right).cast_up()

        cast = ""

        match result.e_type:
            case "u64"|"i64"|"f64":
                self.transpiler.include("math")
                func = "pow"
                cast = "" if result.e_type == "f64" else f"({result.c_type})"
            case "umax"|"imax"|"fmax":
                self.transpiler.include("math")
                func = "powl"
                cast = "" if result.e_type == "fmax" else f"({result.c_type})"
            case "c64":
                self.transpiler.include("complex")
                func = "cpow"
            case "cmax":
                self.transpiler.include("tgmath")
                func = "cpowl"

        return result.new(f"({cast}{func}({left}, {right}))")
