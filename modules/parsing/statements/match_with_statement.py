from ..node import Node

class MatchWithStatement(Node):
    @classmethod
    def construct(cls, children):
        if not children.next_token.has("match"):
            return None

        children.take()
        children.make("Expression")
        children.expecting_has(":")

        if children.next_token.has("pass"):
            children.take()
            children.expecting_has("\n")
            return cls(children)

        children.expecting_has("\n")
        children.take_empty_lines()
        children.expecting_indent()

        if children.next_token.has("pass"):
            children.take()
            children.expecting_has("\n")
            return cls(children)

        while children.next_token.has("with"):
            children.take()
            children.make("ConstantExpression")
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
