from ..node import Node

class Expression(Node):
    @Node.binary_operation([","], "AssignmentExpression")
    def construct(self, parser):
        pass
