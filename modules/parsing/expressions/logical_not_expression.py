from .comparative_expression import ComparativeExpression
from ..node import Node

class LogicalNotExpression(Node):
    @property
    def nodes(self) -> list:
        return [self.keyword, self.expression]

    def __init__(self, keyword, expression):
        self.keyword = keyword
        self.expression = expression

    @classmethod
    def construct(cls):
        if not cls.parser.next.has("not"):
            return ComparativeExpression.construct()

        keyword = cls.parser.take()
        return cls(keyword, cls.construct())

    def transpile(self):
        expression = self.expression.transpile().operate(self, boolean = True)
        return expression.add("!(", ")").cast("bool")
