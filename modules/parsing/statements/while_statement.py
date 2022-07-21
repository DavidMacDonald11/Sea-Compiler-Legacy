from ..node import Node

class WhileStatement(Node):
    def construct(self, parser):
        if parser.next.of("Identifier"):
            parser.take()

            if not parser.next.has("while"):
                parser.untake()
                return None

        if not parser.next.has("while"):
            return None

        parser.take()
        parser.make("Expression")
        parser.expecting_has(":")
        parser.make("BlockStatement", depth = 1)

        if parser.indent_count() < parser.depth:
            return self

        parser.expecting_indent()

        if parser.next.has("else"):
            parser.take()
            parser.expecting_has(":")
            parser.make("BlockStatement", depth = 1)

        return self
