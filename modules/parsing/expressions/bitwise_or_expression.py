from ..node import Node, binary_operation

class BitwiseOrExpression(Node):
    @classmethod
    @binary_operation(["|"], "BitwiseXorExpression")
    def construct(cls, children):
        pass
