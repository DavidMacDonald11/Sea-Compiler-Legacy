from ..node import Node

class StructureDeclaration(Node):
    def construct(self, parser):
        i = type(parser).index
        parser.make("StorageClassSpecifier")

        if not parser.next.has("enum", "struct", "union"):
            type(parser).index = i
            return parser.make("FunctionDeclaration")

        parser.take()
        parser.expecting_of("Identifier")
        parser.expecting_has(":")
        parser.make("BlockStatement", depth = 1)

        return self
