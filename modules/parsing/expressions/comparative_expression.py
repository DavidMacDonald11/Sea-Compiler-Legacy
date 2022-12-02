from transpiling.expression import Expression
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
        result = Expression.resolve(left, right).cast("bool")
        operator = self.operator.string

        if not isinstance(self.left, ComparativeExpression):
            self.verify_types(left, operator, right)
            return result.new(f"{left} {operator} {right}")

        left_arg = self.left.right.transpile()
        self.verify_types(left_arg, operator, right)

        return result.new(f"{left} && {left_arg} {operator} {right}")

    def verify_types(self, left, operator, right):
        if operator not in (">", ">=", "<", "<="): return

        if "cplex" in Expression.resolve(left, right).kind:
            kind1, kind2 = left.kind, right.kind

            if "imag" in kind1 and "imag" not in kind2 or "imag" in kind2 and "imag" not in kind1:
                message = "between 'real' and 'imag' values"
            else:
                message = "on a 'cplex' value"

            self.transpiler.warnings.error(self, "".join((
                f"Cannot perform operation '{operator}' {message}. ",
                "(Consider using '|| ||' brackets to get real value)"
            )))
