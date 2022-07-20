from ..node import Node

class IfStatement(Node):
    @classmethod
    def construct(cls, children):
        if not children.next_token.has("if"):
            return None

        children.take()
        children.make("Expression")
        children.expecting_has(":")
        children.make("BlockStatement", children.next(1))

        if children.indent_count() < children.depth:
            return cls(children)

        children.expecting_indent()
        else_if = True

        while else_if and children.next_token.has("else"):
            children.take()

            if children.next_token.has("if"):
                children.take()
                children.make("Expression")
            else:
                else_if = False

            children.expecting_has(":")
            children.make("BlockStatement", children.next(1))

            if children.indent_count() < children.depth:
                return cls(children)

            children.expecting_indent()

        return cls(children)
