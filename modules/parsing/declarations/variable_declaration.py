from ..node import Node

class VariableDeclaration(Node):
    @classmethod
    def construct(cls, children):
        children.make("ElementDeclaration")

        if children.next_token.has("="):
            children.take()
            children.make("Initializer")

        return cls(children)
