from .bitwise_and_expression import BitwiseAndExpression
from ..node import BinaryOperation

class BitwiseXorExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["$"], BitwiseAndExpression)

    def transpile(self):
        return self.transpile_binary("^", bitwise = True)
