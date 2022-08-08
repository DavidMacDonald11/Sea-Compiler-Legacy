from .postfix_expression import PostfixExpression
from ..node import BinaryOperation

class ExponentialExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["^"], PostfixExpression, cls.parser.unary_expression)

    def transpile(self, transpiler):
        left = self.left.transpile(transpiler)
        right = self.right.transpile(transpiler)

        return left ** right
