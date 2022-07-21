from ..node import Node

class BitwiseOrExpression(Node):
    @Node.binary_operation(["|"], "BitwiseXorExpression")
    def construct(self, parser):
        pass
