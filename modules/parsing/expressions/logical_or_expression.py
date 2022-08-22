from .logical_and_expression import LogicalAndExpression
from ..node import BinaryOperation

class LogicalOrExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["or"], LogicalAndExpression)

    def transpile(self):
        return self.transpile_binary("||", boolean = True)
