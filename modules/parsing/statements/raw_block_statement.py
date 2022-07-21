from ..node import Node

class RawBlockStatement(Node):
    @classmethod
    def construct(cls, children):
        if not children.next_token.has("clang", "asm"):
            return None

        children.take()
        children.expecting_has("block")
        children.expecting_has(":")
        children.take_comments()
        children.expecting_line_end()
        children.take_empty_lines()
        empty = True

        while children.indent_count() >= children.depth:
            empty = False
            children.expecting_indent(atleast = True)

            if children.next_token == ("Keyword", "pass"):
                children.take()
                children.expecting_line_end()
                children.take_empty_lines()
                break

            children.expecting_of("Raw")
            children.expecting_line_end()
            children.take_empty_lines()

        node = cls(children)

        if empty:
            node.mark()
            children.warn("Empty block")

        return node
