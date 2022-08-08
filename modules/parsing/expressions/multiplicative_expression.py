from .unary_expression import UnaryExpression
from ..node import BinaryOperation

class MultiplicativeExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["*", "/"], UnaryExpression)

    def transpile(self, transpiler):
        left = self.left.transpile(transpiler)
        right = self.right.transpile(transpiler)

        if self.operator.has("/"):
            left_int = isinstance(left, int)
            right_int = isinstance(right, int)
            return (left // right) if left_int and right_int else (left / right)

        return (left * right) if self.operator.has("*") else (right / left)
