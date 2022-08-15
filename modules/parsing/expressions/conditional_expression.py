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
        le_type, left = self.left.transpile()
        c_type, condition = self.condition.transpile()
        re_type, right = self.right.transpile()
        e_type = self.transpiler.resolve_type(le_type, re_type)

        if c_type != "bool":
            self.transpiler.warnings.error(self, "".join((
                "Cannot perform conditional statment on non-boolean condition.",
                " (Consider using the '?' operator to get boolean value)"
            )))

            return (e_type, f"/*({condition}) ? {left} :*/ {right}")

        return (e_type, f"({condition}) ? {left} : {right}")
