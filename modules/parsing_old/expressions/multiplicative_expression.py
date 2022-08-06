from ..node import Node

class MultiplicativeExpression(Node):
    @Node.binary_operation(["*", "/", "mod"], "CastExpression")
    def construct(self, parser):
        pass
