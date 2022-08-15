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
        e_type, expression = self.expression.transpile()

        if e_type != "bool":
            self.transpiler.warnings.error(self, "Cannot perform negation of non-boolean value")
            return f"/*not*/ ({expression})"

        return ("bool", f"!({expression})")
