from .remainder_expression import RemainderExpression
from ..node import BinaryOperation

class ThreeWayComparisonExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["<=>"], RemainderExpression)

    def transpile(self):
        left = self.left.transpile().operate(self)
        right = self.right.transpile().operate(self)
        result = self.transpiler.resolve(left, right).cast_up()

        return result.new(f"(({left}) - ({right}))")
