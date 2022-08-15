from .logical_or_expression import LogicalOrExpression
from ..node import Node

class Expression(Node):
    @classmethod
    def construct(cls):
        return LogicalOrExpression.construct()
