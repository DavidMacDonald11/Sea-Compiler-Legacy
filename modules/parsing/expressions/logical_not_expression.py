from ..node import Node

class LogicalNotExpression(Node):
    @classmethod
    def construct(cls, children):
        if not children.next_token.has("not"):
            return children.make("ComparativeExpression")

        children.take()
        children.make("LogicalNotExpression")

        return cls(children)
