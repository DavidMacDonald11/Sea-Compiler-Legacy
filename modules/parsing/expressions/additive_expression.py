from .multiplicative_expression import MultiplicativeExpression
from ..node import BinaryOperation

class AdditiveExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["+", "-"], MultiplicativeExpression)

    def transpile(self, transpiler):
        left = self.left.transpile(transpiler)
        right = self.right.transpile(transpiler)

        return (left + right) if self.operator.has("+") else (left - right)
