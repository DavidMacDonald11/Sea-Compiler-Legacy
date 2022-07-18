from ..node import Node

class PrefixDeviationExpression(Node):
    @classmethod
    def construct(cls, children):
        if not children.next_token.has("++", "--"):
            return children.make("PostfixExpression")

        children.take()
        children.make("PrefixDeviationExpression")

        return cls(children)
