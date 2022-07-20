from ..node import Node

class TemplateDeclaration(Node):
    @classmethod
    def construct(cls, children):
        if not children.next_token.has("template"):
            return None

        children.take()
        children.expecting_has("with")

        empty = True

        while children.next_token.has("type"):
            empty = False
            children.expecting_has("type")
            children.expecting_of("Identifier")

            if children.next_token.has(","):
                children.take()

        children.expecting_line_end()
        node = cls(children)

        if empty:
            node.mark()
            children.warn("Cannot have empty template")

        return node
