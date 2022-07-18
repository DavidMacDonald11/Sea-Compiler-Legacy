from ..node import Node, binary_operation

class LogicalOrExpression(Node):
    @classmethod
    @binary_operation(["or"], "LogicalAndExpression")
    def construct(cls, children):
        pass
