from ..node import Node

class Statement(Node):
    def construct(self, parser):
        if parser.take_if_empty_line() is not None:
            return self

        node = parser.make("IfStatement")
        node = node or parser.make("MatchWithStatement", depth = 1)
        node = node or parser.make("ManageStatement")
        node = node or parser.make("WhileStatement")
        node = node or parser.make("DoWhileStatement")
        node = node or parser.make("ForStatement")
        node = node or parser.make("Block")
        node = node or parser.make("RawBlockStatement", depth = 1)
        node = node or parser.make("TemplateDeclaration")
        node = node or parser.make("DecoratorDeclaration")

        if node is not None:
            return node

        if (node := parser.make("BlockableStatement")) is not None:
            node.mark()
            parser.warn(f"Unexpected {node.children.nodes[0].string} statement")
            return self

        return parser.make("StructureDeclaration", parser)
