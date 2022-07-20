from ..node import Node

class StructureDeclaration(Node):
    @classmethod
    def construct(cls, children):
        i = children.parser.i
        children.make("StorageClassSpecifier")

        if not children.next_token.has("enum", "struct", "union"):
            children.parser.i = i
            return children.make("FunctionDeclaration")

        children.take()
        children.expecting_has("Identifier")
        children.expecting_has(":")
        children.make("BlockStatement", children.next(1))

        return cls(children)
