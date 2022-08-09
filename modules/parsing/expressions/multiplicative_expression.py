from .unary_expression import UnaryExpression
from ..node import BinaryOperation

class MultiplicativeExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["*", "/"], UnaryExpression)
