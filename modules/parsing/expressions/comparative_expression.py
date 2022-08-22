from lexing.token import COMPARATIVE_OPERATORS
from .three_way_comparison_expression import ThreeWayComparisonExpression
from ..node import BinaryOperation

class ComparativeExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(COMPARATIVE_OPERATORS, ThreeWayComparisonExpression)

    def transpile(self):
        left = self.left.transpile().operate(self)
        right = self.right.transpile().operate(self)
        result = self.transpiler.expression.resolve(left, right).cast("bool")

        if not isinstance(self.left, ComparativeExpression):
            return result.new(f"{left} {self.operator.string} {right}")

        left_arg = self.left.right.transpile()
        return result.new(f"{left} && {left_arg} {self.operator.string} {right}")
