from ..node import Node

class LineStatement(Node):
    def construct(self, parser):
        if parser.next.has("alias"):
            return parser.make("AliasStatement")

        if parser.next.has("asert"):
            return parser.make("StaticAssertStatement")

        if parser.next.has("static"):
            static = parser.take()

            if not parser.next.has("assert"):
                parser.untake()
            else:
                parser = parser.new()
                parser.children += static
                return parser.make("StaticAssertStatement", parser)

        parser.make("LineStatementComponent")
        parser.expecting_line_end()

        return self
