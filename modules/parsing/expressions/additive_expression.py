from .multiplicative_expression import MultiplicativeExpression
from ..node import BinaryOperation

class AdditiveExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["+", "-"], MultiplicativeExpression)
