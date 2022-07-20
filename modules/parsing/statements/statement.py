from ..node import Node

class Statement(Node):
    @classmethod
    def construct(cls, children):
        empty_line = children.check_empty_line()

        if empty_line is not None:
            return cls(empty_line)

        node = children.make("IfStatement", children.next())
        node = node or children.make("MatchWithStatement", children.next(1))
        node = node or children.make("ManageStatement", children.next())
        node = node or children.make("WhileStatement", children.next())
        node = node or children.make("DoWhileStatement", children.next())
        node = node or children.make("ForStatement", children.next())
        node = node or children.make("Block", children.next())
        node = node or children.make("TemplateDeclaration", children.next())
        node = node or children.make("DecoratorDeclaration", children.next())

        if node is not None:
            return cls(children)

        blockable = children.make("BlockableStatement")

        if blockable is not None:
            blockable.mark()
            children.warn(f"Unexpected {blockable.children.nodes[0].string} statement")
            return cls(children)

        return children.make("StructureDeclaration", children)
