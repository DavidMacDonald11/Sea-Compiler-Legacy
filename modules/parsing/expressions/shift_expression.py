from .additive_expression import AdditiveExpression
from ..node import BinaryOperation

class ShiftExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["<<", ">>"], AdditiveExpression)

    def transpile(self):
        return self.transpile_binary(self.operator.string, bitwise = True)
