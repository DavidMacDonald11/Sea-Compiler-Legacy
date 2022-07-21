from ..node import Node

class FunctionDeclaration(Node):
    def construct(self, parser):
        i = type(parser).index
        parser.make("FunctionSpecifier")

        if not parser.next.has("func"):
            type(parser).index = i
            return parser.make("LineStatement")

        parser.take()

        if not parser.next.of("Identifier"):
            type(parser).index = i
            return parser.make("LineStatement")

        parser.take()
        parser.expecting_has("(")

        if not parser.next.has(")"):
            parser.make("FunctionVariadicList")

        parser.expecting_has(")")

        if parser.next.has("->"):
            parser.take()
            parser.make("TypeName")

        parser.expecting_has(":")
        parser.make("BlockStatement", depth = 1)

        return self
