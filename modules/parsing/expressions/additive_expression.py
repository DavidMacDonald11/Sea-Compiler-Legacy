from ..node import Node

class AdditiveExpression(Node):
    @Node.binary_operation(["+", "-"], "MultiplicativeExpression")
    def construct(self, parser):
        pass
