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
        operator = self.operator.string
        result = self.transpiler.expression.resolve(left, right).cast("bool")

        if not isinstance(self.left, ComparativeExpression):
            self.verify_types(left, operator, right)
            return result.new(f"{left} {operator} {right}")

        left_arg = self.left.right.transpile()
        self.verify_types(left_arg, operator, right)

        return result.new(f"{left} && {left_arg} {operator} {right}")

    def verify_types(self, left, operator, right):
        if operator not in (">", ">=", "<", "<="): return

        if self.transpiler.expression.resolve(left, right).e_type in ("c64", "cmax"):
            self.transpiler.warnings.error(self, "".join((
                f"Cannot perform operation {operator} on cplex value. ",
                "(Consider using '|| ||' brackets to get real value)"
            )))
