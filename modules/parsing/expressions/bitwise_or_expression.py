from .bitwise_xor_expression import BitwiseXorExpression
from ..node import BinaryOperation

class BitwiseOrExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["|"], BitwiseXorExpression)

    def transpile(self):
        return self.transpile_binary(self.operator.string, bitwise = True)
