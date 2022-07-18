from ..node import Node, binary_operation

class MultiplicativeExpression(Node):
    @classmethod
    @binary_operation(["*", "/", "mod"], "CastExpression")
    def construct(cls, children):
        pass
