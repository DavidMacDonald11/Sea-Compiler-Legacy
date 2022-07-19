from ..node import Node

class Declaration(Node):
    @classmethod
    def construct(cls, children):
        children.make("VariableDeclaration")

        while children.next_token.has(","):
            children.take()
            children.make("VariableDeclaration")

        return cls(children)
