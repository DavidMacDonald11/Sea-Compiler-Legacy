from .additive_expression import AdditiveExpression
from ..node import BinaryOperation

class ShiftExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["<<", ">>"], AdditiveExpression)

    def transpile(self, transpiler):
        left = self.left.transpile(transpiler)
        right = self.right.transpile(transpiler)

        return (left << right) if self.operator.has("<<") else (right >> left)
