from .cast_expression import CastExpression
from ..node import Node

class Expression(Node):
    @classmethod
    def construct(cls):
        return CastExpression.construct()
