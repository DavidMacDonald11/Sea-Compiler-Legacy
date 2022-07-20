from ..node import Node

class DoWhileStatement(Node):
    @classmethod
    def construct(cls, children):
        label = None

        if children.next_token.of("Identifier"):
            label = children.take()

            if not children.next_token.has("do"):
                children.untake()
                return None

        if not children.next_token.has("do"):
            return None

        children.take()

        if children.next_token.of("Identifier"):
            post_label = children.take()

            if label is not None:
                label.mark()
                post_label.mark()
                children.warn("Cannot double label do-while statement")

        children.expecting_has(":")
        children.take_comments()

        if children.next_token.has("\n", ""):
            children.make("BlockStatement", children.next(1))
            children.expecting_indent()
        else:
            blockable = children.make("BlockableStatementComponent")

            if blockable is None:
                children.make("LineStatementComponent")

            if children.next_token.has("\n"):
                children.take()
                children.take_empty_lines()
                children.expecting_indent()

        children.expecting_has("while")
        children.make("Expression")
        children.take_comments()
        children.expecting_line_end()

        if children.indent_count() < children.depth:
            return cls(children)

        children.expecting_indent()

        if children.next_token.has("else"):
            children.take()
            children.expecting_has(":")
            children.make("BlockStatement", children.next(1))

        return cls(children)
