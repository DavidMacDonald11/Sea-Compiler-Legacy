from ..node import Node

class ForStatement(Node):
    def construct(self, parser):
        if parser.next.of("Identifier"):
            parser.take()

            if not parser.next.has("for"):
                parser.untake()
                return None

        if not parser.next.has("for"):
            return None

        parser.take()
        parser.make("ElementDeclaration")
        parser.expecting_has("in")
        parser.make("Initializer")
        parser.expecting_has(":")
        parser.make("BlockStatement", depth = 1)

        if parser.indent_count() < parser.depth:
            return self

        if parser.next.has("else"):
            parser.take()
            parser.expecting_has(":")
            parser.make("BlockStatement", depth = 1)

        return self
