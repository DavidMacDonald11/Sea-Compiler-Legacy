from .logical_not_expression import LogicalNotExpression
from ..node import BinaryOperation

class LogicalAndExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["and"], LogicalNotExpression)

    def transpile(self):
        return self.transpile_binary("&&", boolean = True)
