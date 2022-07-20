from ..node import Node

class WhileStatement(Node):
    @classmethod
    def construct(cls, children):
        if children.next_token.of("Identifier"):
            children.take()

            if not children.next_token.has("while"):
                children.untake()
                return None

        if not children.next_token.has("while"):
            return None

        children.take()
        children.make("Expression")
        children.expecting_has(":")
        children.make("BlockStatement", children.next(1))

        if children.indent_count() < children.depth:
            return cls(children)

        children.expecting_indent()

        if children.next_token.has("else"):
            children.take()
            children.expecting_has(":")
            children.make("BlockStatement", children.next(1))

        return cls(children)
