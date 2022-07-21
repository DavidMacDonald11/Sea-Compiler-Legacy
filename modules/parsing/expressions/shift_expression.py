from ..node import Node

class ShiftExpression(Node):
    @Node.binary_operation(["<<", ">>"], "AdditiveExpression")
    def construct(self, parser):
        pass
