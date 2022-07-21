from ..node import Node

class MatchWithStatement(Node):
    def construct(self, parser):
        if not parser.next.has("match"):
            return None

        parser.take()
        parser.make("Expression")
        parser.expecting_has(":")

        if parser.next.has("pass"):
            parser.take()
            parser.expecting_has("\n")
            return self

        parser.expecting_has("\n")
        parser.take_empty_lines()
        parser.expecting_indent()

        if parser.next.has("pass"):
            parser.take()
            parser.expecting_has("\n")
            return self

        while parser.next.has("with"):
            parser.take()
            parser.make("ConstantExpression")
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
