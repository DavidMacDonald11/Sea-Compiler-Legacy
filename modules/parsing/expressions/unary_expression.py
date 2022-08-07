from lexing.token import PREFIX_UNARY_OPERATORS
from .exponential_expression import ExponentialExpression
from ..node import Node

class UnaryExpression(Node):
    @property
    def nodes(self):
        return [self.operator, self.expression]

    def __init__(self, operator, expression):
        self.operator = operator
        self.expression = expression

    @classmethod
    def construct(cls):
        if not cls.parser.next.has(*PREFIX_UNARY_OPERATORS):
            return ExponentialExpression.construct()

        operator = cls.parser.take()
        return cls(operator, cls.construct())
