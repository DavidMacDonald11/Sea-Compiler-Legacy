from ..node import Node

class PrefixDeviationExpression(Node):
    def construct(self, parser):
        if not parser.next.has("++", "--"):
            return parser.make("PostfixExpression")

        parser.take()
        parser.make("PrefixDeviationExpression")

        return self
