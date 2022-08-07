from .additive_expression import AdditiveExpression
from ..node import BinaryOperation

class ShiftExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["<<", ">>"], AdditiveExpression)
