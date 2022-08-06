from ..node import Node

class BlockStatement(Node):
    def construct(self, parser):
        parser.take_any_comments()

        if not parser.next.has("\n"):
            if parser.make("BlockableStatement") is None:
                parser.make("LineStatement")

            return self

        parser.take()
        parser.take_any_empty_lines()
        empty = True

        while parser.indent_count() == parser.depth:
            empty = False
            parser.expecting_indent()

            if parser.make("BlockableStatement") is None:
                parser.make("Statement")

            parser.take_any_empty_lines()

        if empty:
            self.mark()
            parser.warn("Block cannot be empty; use pass")

        return self
