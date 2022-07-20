from ..node import Node

class BlockStatement(Node):
    @classmethod
    def construct(cls, children):
        children.take_comments()

        if not children.next_token.has("\n"):
            blockable = children.make("BlockableStatement")

            if blockable is None:
                children.make("LineStatement")

            return cls(children)

        children.take()
        children.take_empty_lines()
        empty = True

        while children.indent_count() == children.depth:
            empty = False
            children.expecting_indent()
            blockable = children.make("BlockableStatement")

            if blockable is None:
                children.make("Statement", children.next())

            children.take_empty_lines()

        node = cls(children)

        if empty:
            node.mark()
            children.warn("Empty block")

        return node
