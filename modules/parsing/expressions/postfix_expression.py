from lexing.token import POSTFIX_UNARY_OPERATORS
from .primary_expression import PrimaryExpression
from ..node import Node

class PostfixExpression(Node):
    @property
    def nodes(self) -> list:
        return [self.expression, self.operator]

    def __init__(self, expression, operator):
        self.expression = expression
        self.operator = operator

    @classmethod
    def construct(cls):
        node = PrimaryExpression.construct()

        if not cls.parser.next.has(*POSTFIX_UNARY_OPERATORS):
            return node

        while cls.parser.next.has(*POSTFIX_UNARY_OPERATORS):
            node = cls(node, cls.parser.take())

        return node

    def transpile(self, transpiler):
        expression = self.expression.transpile(transpiler)

        if self.operator.has("++", "--"):
            return expression + (1 if self.operator.has("++") else -1)

        if self.operator.has("%"):
            return expression * .01

        # TODO factorial
