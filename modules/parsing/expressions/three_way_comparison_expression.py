from .remainder_expression import RemainderExpression
from ..node import BinaryOperation

class ThreeWayComparisonExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["<=>"], RemainderExpression)

    def transpile(self):
        le_type, left = self.left.transpile()
        re_type, right = self.right.transpile()
        e_type = self.transpiler.resolve_type(le_type, re_type)

        return (e_type, f"(({left}) - ({right}))")
