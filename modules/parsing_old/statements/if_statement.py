from ..node import Node

class IfStatement(Node):
    def construct(self, parser):
        if not parser.next.has("if"):
            return None

        parser.take()
        parser.make("Expression")
        parser.expecting_has(":")
        parser.make("BlockStatement", depth = 1)

        if parser.indent_count() < parser.depth:
            return self

        parser.expecting_indent()
        else_if = True

        while else_if and parser.next.has("else"):
            parser.take()

            if parser.next.has("if"):
                parser.take()
                parser.make("Expression")
            else:
                else_if = False

            parser.expecting_has(":")
            parser.make("BlockStatement", depth = 1)

            if parser.indent_count() < parser.depth:
                return self

            parser.expecting_indent()

        return self
