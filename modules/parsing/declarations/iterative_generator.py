from ..node import Node

class IterativeGenerator(Node):
    @classmethod
    def construct(cls, children):
        if not children.next_token.has("yield"):
            return None

        children.take()
        children.make("Initializer")
        children.expecting_has("for")
        children.make("ElementDeclaration")
        children.expecting_has("in")
        children.make("SafeInitializer")

        if children.next_token.has("if"):
            children.take()
            children.make("Expression")

        return cls(children)
