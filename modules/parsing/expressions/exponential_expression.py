from .postfix_expression import PostfixExpression
from ..node import BinaryOperation

class ExponentialExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["^"], PostfixExpression, cls.parser.unary_expression)

    def transpile(self):
        le_type, left = self.left.transpile()
        re_type, right = self.right.transpile()
        e_type = self.transpiler.resolve_type(le_type, re_type)

        cast = ""

        match e_type:
            case "u64"|"i64"|"f64":
                self.transpiler.include("math")
                func = "pow"
                cast = "" if e_type == "f64" else f"({self.transpiler.safe_type(e_type)})"
            case "umax"|"imax"|"fmax":
                self.transpiler.include("math")
                func = "powl"
                cast = "" if e_type == "fmax" else f"({self.transpiler.safe_type(e_type)})"
            case "c64":
                self.transpiler.include("complex")
                func = "cpow"
            case "cmax":
                self.transpiler.include("tgmath")
                func = "cpowl"

        return (e_type, f"({cast}{func}({left}, {right}))")
