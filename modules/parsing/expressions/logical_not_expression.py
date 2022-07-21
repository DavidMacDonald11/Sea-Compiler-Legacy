from ..node import Node

class LogicalNotExpression(Node):
    def construct(self, parser):
        if not parser.next.has("not"):
            return parser.make("ComparativeExpression")

        parser.take()
        parser.make("LogicalNotExpression")

        return self
