from .logical_or_expression import LogicalOrExpression
from ..node import Node

class ConditionalExpression(Node):
    @property
    def nodes(self) -> list:
        return [self.left, self.condition, self.right]

    def __init__(self, left, condition, right):
        self.left = left
        self.condition = condition
        self.right = right

    @classmethod
    def construct(cls):
        left = LogicalOrExpression.construct()

        while cls.parser.next.has("if"):
            cls.parser.take()
            condition = cls.parser.expression.construct()
            cls.parser.expecting_has("else")
            left = cls(left, condition, cls.construct())

        return left

    def transpile(self):
        left = self.left.transpile().operate(self)
        condition = self.condition.transpile()
        right = self.right.transpile().operate(self)
        result = self.transpiler.expression.resolve(left, right).cast_up()

        if condition.e_type != "bool":
            self.transpiler.warnings.error(self, "".join((
                "Cannot perform conditional statment with non-boolean condition.",
                " (Consider using the '?' operator to get boolean value)"
            )))

            return result.new(f"/*({condition}) ? {left} :*/ {right}")

        return result.new(f"({condition}) ? {left} : {right}")
