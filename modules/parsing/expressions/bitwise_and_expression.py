from .shift_expression import ShiftExpression
from ..node import BinaryOperation

class BitwiseAndExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["&"], ShiftExpression)
