from ..expressions.expression import Expression
from ..expressions.unary_expression import OwnershipExpression
from ..node import Node

class ExpressionStatement(Node):
    @property
    def nodes(self) -> list:
        return [self.expression]

    def __init__(self, expression):
        self.expression = expression

    # def tree_repr(self, prefix):
    #     return self.expression.tree_repr(prefix)

    @classmethod
    def construct(cls):
        expression = Expression.construct()
        cls.parser.expecting_has(r"\n", "EOF")
        return cls(expression)

    def transpile(self):
        if isinstance(self.expression, OwnershipExpression):
            message = "Must assign identifier to result of ownership expression"
            self.transpiler.warnings.error(self, message)

        return self.expression.transpile()
