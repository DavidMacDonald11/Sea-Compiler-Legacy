from .conditional_expression import ConditionalExpression
from ..node import Node

class Expression(Node):
    @classmethod
    def construct(cls):
        return ConditionalExpression.construct()
