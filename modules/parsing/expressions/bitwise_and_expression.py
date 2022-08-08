from .shift_expression import ShiftExpression
from ..node import BinaryOperation

class BitwiseAndExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["&"], ShiftExpression)

    def transpile(self, transpiler):
        left = self.left.transpile(transpiler)
        right = self.right.transpile(transpiler)

        return left & right
