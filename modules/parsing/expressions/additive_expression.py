from ..node import Node, binary_operation

class AdditiveExpression(Node):
    @classmethod
    @binary_operation(["+", "-"], "MultiplicativeExpression")
    def construct(cls, children):
        pass
