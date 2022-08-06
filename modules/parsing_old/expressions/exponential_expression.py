from ..node import Node

class ExponentialExpression(Node):
    def construct(self, parser):
        node = parser.make("PrefixDeviationExpression")

        if not parser.next.has("**"):
            return node

        parser.take()
        parser.make("CastExpression")

        return self
