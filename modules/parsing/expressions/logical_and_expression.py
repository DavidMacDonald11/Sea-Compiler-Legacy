from ..node import Node, binary_operation

class LogicalAndExpression(Node):
    @classmethod
    @binary_operation(["and"], "LogicalNotExpression")
    def construct(cls, children):
        pass
