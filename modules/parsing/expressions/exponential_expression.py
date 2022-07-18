from ..node import Node

class ExponentialExpression(Node):
    @classmethod
    def construct(cls, children):
        node = children.make("PrefixDeviationExpression")

        if not children.next_token.has("**"):
            return node

        children.take()
        children.make("CastExpression")

        return cls(children)
