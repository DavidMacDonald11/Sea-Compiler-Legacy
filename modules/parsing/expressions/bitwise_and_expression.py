from ..node import Node, binary_operation

class BitwiseAndExpression(Node):
    @classmethod
    @binary_operation(["&"], "ShiftExpression")
    def construct(cls, children):
        pass
