from ..node import Node

class DefineStatement(Node):
    def construct(self, parser):
        if not parser.next.has("define", "redefine", "undefine"):
            return None

        keyword = parser.take()
        parser.expecting_of("Identifier")

        if keyword.has("undefine") or not parser.next.has("as"):
            parser.expecting_line_end()
            return self

        parser.take()
        parser.make("ConstantExpression")
        parser.expecting_line_end()

        return self
