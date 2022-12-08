from transpiling.expression import Expression
from .logical_and_expression import LogicalAndExpression
from ..node import BinaryOperation

class LogicalXorExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["xor"], LogicalAndExpression)

    def transpile(self):
        left = self.left.transpile().operate(self, boolean = True)
        right = self.right.transpile().operate(self, boolean = True)
        result = Expression.resolve(left, right).cast_up()
        result.new(f"!({left} && {right}) && ({left} || {right})")

        return result.cast("bool")
