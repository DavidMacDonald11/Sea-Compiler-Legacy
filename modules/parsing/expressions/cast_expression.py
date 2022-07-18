from ..node import Node

class CastExpression(Node):
    @classmethod
    def construct(cls, children):
        if children.next_token.has("("):
            children.ignore()

            nextt = children.next_token
            if nextt.of("Keyword") and not nextt.has("not") or nextt.has("+"):
                children.take_previous()
                children.make("TypeName")
                children.expecting_has(")")
                children.make("CastExpression")

                return cls(children)

            children.unignore()

        return children.make("UnaryExpression")
