from ..node import Node

class RawBlockStatement(Node):
    def construct(self, parser):
        if not parser.next.has("clang", "asm"):
            return None

        parser.take()
        parser.expecting_has("block")
        parser.expecting_has(":")
        parser.expecting_line_end()
        parser.take_any_empty_lines()
        empty = True

        while parser.indent_count() >= parser.depth:
            empty = False
            parser.expecting_indent(atleast = True)

            if parser.next == ("Keyword", "pass"):
                parser.take()
                parser.expecting_line_end()
                parser.take_any_empty_lines()
                break

            parser.expecting_of("Raw")
            parser.expecting_line_end()
            parser.take_any_empty_lines()

        if empty:
            self.mark()
            parser.warn("Block cannot be empty; use pass")

        return self
