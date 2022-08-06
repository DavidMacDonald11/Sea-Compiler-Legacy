from ..node import Node

class IncludeStatement(Node):
    def construct(self, parser):
        if not parser.next.has("include"):
            return None

        parser.take()

        if not parser.next.has("\"", "<"):
            parser.expecting_of("FilePath")
            parser.take_any_comments()
            parser.expecting_line_end()

            return self

        parser.take()
        parser.expecting_of("FilePath")
        parser.expecting_has("\"", ">")
        parser.take_any_comments()
        parser.expecting_line_end()

        return self
