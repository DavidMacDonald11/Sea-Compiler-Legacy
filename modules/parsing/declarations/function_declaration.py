from ..node import Node

class FunctionDeclaration(Node):
    @classmethod
    def construct(cls, children):
        i = children.parser.i
        children.make("FunctionSpecifier")

        if not children.next_token.of("Identifier"):
            children.parser.i = i
            return children.make("LineStatement")

        children.take()

        if not children.next_token.has("("):
            children.parser.i = i
            return children.make("LineStatement")

        children.take()

        if not children.next_token.has(")"):
            children.make("FunctionVariadicList")

        children.expecting_has(")")

        if children.next_token.has("->"):
            children.take()
            children.make("TypeName")

        children.expecting_has(":")
        children.make("BlockStatement", children.next(1))

        return cls(children)
