from ..node import Node

class VariableDeclaration(Node):
    def construct(self, parser):
        parser.make("ElementDeclaration")

        if parser.next.has("="):
            parser.take()
            parser.make("Initializer")

        return self
