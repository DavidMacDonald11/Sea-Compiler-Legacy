from ..node import Node, binary_operation

class Expression(Node):
    @classmethod
    @binary_operation([","], "AssignmentExpression")
    def construct(cls, children):
        pass
