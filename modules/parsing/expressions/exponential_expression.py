from .postfix_expression import PostfixExpression
from ..node import BinaryOperation

class ExponentialExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["^"], PostfixExpression, cls.parser.unary_expression)

    def transpile(self, transpiler):
        left = self.left.transpile(transpiler)
        e_type = transpiler.expression_type
        right = self.right.transpile(transpiler)

        transpiler.expression_type = e_type
        transpiler.include("math")
        cast = ""

        if e_type != "f64":
            cast = "(i64)" if e_type == "i64" else "(u64)"

        return f"({cast}pow({left}, {right}))"
