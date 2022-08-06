from ..node import Node

class ConditionalExpression(Node):
    def construct(self, parser):
        node = parser.make("LogicalOrExpression")

        if not parser.next.has("if"):
            return node

        parser.take()
        parser.make("Expression")
        parser.expecting_has("else")
        parser.make("ConditionalExpression")

        return self
