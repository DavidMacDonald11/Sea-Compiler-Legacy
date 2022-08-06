from ..node import Node

class BitwiseAndExpression(Node):
    @Node.binary_operation(["&"], "ShiftExpression")
    def construct(self, parser):
        pass
