from ..node import Node

class Declaration(Node):
    def construct(self, parser):
        parser.make("VariableDeclaration")

        while parser.next.has(","):
            parser.take()
            parser.make("VariableDeclaration")

        return self
