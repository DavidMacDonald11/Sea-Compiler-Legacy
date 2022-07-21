from ..node import Node

class IterativeGenerator(Node):
    def construct(self, parser):
        if not parser.next.has("yield"):
            return None

        parser.take()
        parser.make("Initializer")
        parser.expecting_has("for")
        parser.make("ElementDeclaration")
        parser.expecting_has("in")
        parser.make("SafeInitializer")

        if parser.next.has("if"):
            parser.take()
            parser.make("Expression")

        return self
