from ..node import Node, binary_operation

class BitwiseXorExpression(Node):
    @classmethod
    @binary_operation(["$"], "BitwiseAndExpression")
    def construct(cls, children):
        pass
