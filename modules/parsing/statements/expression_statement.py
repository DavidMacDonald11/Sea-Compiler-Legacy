from ..expressions.expression import Expression
from ..node import Node

class ExpressionStatement(Node):
    @property
    def nodes(self) -> list:
        return [self.expression]

    def __init__(self, expression):
        self.expression = expression

    def tree_repr(self, prefix):
        return self.expression.tree_repr(prefix)

    @classmethod
    def construct(cls):
        expression = Expression.construct()
        return cls(expression)

    def transpile(self):
        expression = self.expression.transpile()

        if expression.ownership is not None:
            message = "Must assign result of ownership expression to an identifier"
            self.transpiler.warnings.error(self, message)

        return expression
