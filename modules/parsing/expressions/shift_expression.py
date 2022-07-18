from ..node import Node, binary_operation

class ShiftExpression(Node):
    @classmethod
    @binary_operation(["<<", ">>"], "AdditiveExpression")
    def construct(cls, children):
        pass
