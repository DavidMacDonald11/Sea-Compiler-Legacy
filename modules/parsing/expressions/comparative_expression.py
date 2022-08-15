from lexing.token import COMPARATIVE_OPERATORS
from .three_way_comparison_expression import ThreeWayComparisonExpression
from ..node import BinaryOperation

class ComparativeExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(COMPARATIVE_OPERATORS, ThreeWayComparisonExpression)

    def transpile(self):
        _, left = self.left.transpile()
        _, right = self.right.transpile()

        if not isinstance(self.left, ComparativeExpression):
            return ("bool", f"{left} {self.operator.string} {right}")

        _, left_arg = self.left.right.transpile()
        return ("bool", f"{left} && {left_arg} {self.operator.string} {right}")
