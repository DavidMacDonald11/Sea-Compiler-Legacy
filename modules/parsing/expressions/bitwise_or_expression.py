from .bitwise_xor_expression import BitwiseXorExpression
from ..node import BinaryOperation

class BitwiseOrExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["|"], BitwiseXorExpression)

    def transpile(self, transpiler):
        left = self.left.transpile(transpiler)
        right = self.right.transpile(transpiler)

        return left | right
