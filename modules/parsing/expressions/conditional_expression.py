from ..node import Node

class ConditionalExpression(Node):
    @classmethod
    def construct(cls, children):
        node = children.make("LogicalOrExpression")

        if not children.next_token.has("if"):
            return node

        children.take()
        children.make("Expression")
        children.expecting_has("else")
        children.make("ConditionalExpression")

        return cls(children)
