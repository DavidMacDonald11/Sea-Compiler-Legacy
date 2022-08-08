from .bitwise_and_expression import BitwiseAndExpression
from ..node import BinaryOperation

class BitwiseXorExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["$"], BitwiseAndExpression)

    def transpile(self, transpiler):
        left = self.left.transpile(transpiler)
        right = self.right.transpile(transpiler)

        return left ^ right
