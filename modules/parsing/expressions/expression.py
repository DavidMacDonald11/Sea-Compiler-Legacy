from .bitwise_or_expression import BitwiseOrExpression
from ..node import Node

class Expression(Node):
    @classmethod
    def construct(cls):
        return BitwiseOrExpression.construct()
