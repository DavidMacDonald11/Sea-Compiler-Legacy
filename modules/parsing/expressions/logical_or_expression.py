from ..node import Node

class LogicalOrExpression(Node):
    @Node.binary_operation(["or"], "LogicalAndExpression")
    def construct(self, parser):
        pass
