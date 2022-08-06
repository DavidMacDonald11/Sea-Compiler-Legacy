from ..node import Node

class LogicalAndExpression(Node):
    @Node.binary_operation(["and"], "LogicalNotExpression")
    def construct(self, parser):
        pass
