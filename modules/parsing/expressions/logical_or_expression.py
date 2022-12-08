from .logical_xor_expression import LogicalXorExpression
from ..node import BinaryOperation

class LogicalOrExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["or"], LogicalXorExpression)

    def transpile(self):
        return self.transpile_binary("||", boolean = True)
