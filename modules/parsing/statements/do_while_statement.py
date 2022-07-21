from ..node import Node

class DoWhileStatement(Node):
    def construct(self, parser):
        label = None

        if parser.next.of("Identifier"):
            label = parser.take()

            if not parser.next.has("do"):
                parser.untake()
                return None

        if not parser.next.has("do"):
            return None

        parser.take()

        if parser.next.of("Identifier"):
            post_label = parser.take()

            if label is not None:
                label.mark()
                post_label.mark()
                parser.warn("Cannot double label do-while statement")

        parser.expecting_has(":")
        parser.take_any_comments()

        if parser.next.has("\n", ""):
            parser.make("BlockStatement", depth = 1)
            parser.expecting_indent()
        else:
            if parser.make("BlockableStatementComponent") is None:
                parser.make("LineStatementComponent")

            if parser.next.has("\n"):
                parser.take()
                parser.take_any_empty_lines()
                parser.expecting_indent()

        parser.expecting_has("while")
        parser.make("Expression")
        parser.expecting_line_end()

        if parser.indent_count() < parser.depth:
            return self

        parser.expecting_indent()

        if parser.next.has("else"):
            parser.take()
            parser.expecting_has(":")
            parser.make("BlockStatement", depth = 1)

        return self
