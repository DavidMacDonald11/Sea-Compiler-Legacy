from .unary_expression import UnaryExpression
from ..node import BinaryOperation

class MultiplicativeExpression(BinaryOperation):
    wrote = []

    @classmethod
    def construct(cls):
        return cls.construct_binary(["*", "/"], UnaryExpression)

    def transpile(self):
        return self.transpile_binary(self.operator.string)
