from ..node import Node

class CastExpression(Node):
    @classmethod
    def construct(cls, children):
        if children.next_token.has("("):
            children.ignore()

            if children.next_token_may_be_type:
                children.take_previous()
                children.make("TypeName")
                children.expecting_has(")")
                children.make("CastExpression")

                return cls(children)

            children.unignore()

        return children.make("UnaryExpression")
