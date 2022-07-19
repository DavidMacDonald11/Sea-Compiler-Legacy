from ..node import Node

class DesignatedInitializer(Node):
    @classmethod
    def construct(cls, children):
        if not children.next_token.has("["):
            children.make("Initializer")

            if children.next_token.has(":"):
                children.take()
                children.make("Initializer")

            return cls(children)

        children.take()
        made_generator = children.make("RangedGenerator") is not None

        if not made_generator:
            children.make("ConstantExpression")

        children.expecting_has("]")
        children.expecting_has(":")
        children.make("Initializer")

        return cls(children)
