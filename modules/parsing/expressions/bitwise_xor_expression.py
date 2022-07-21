from ..node import Node

class BitwiseXorExpression(Node):
    @Node.binary_operation(["$"], "BitwiseAndExpression")
    def construct(self, parser):
        pass
