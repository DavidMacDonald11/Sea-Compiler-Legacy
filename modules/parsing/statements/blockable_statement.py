from ..node import Node

class BlockableStatement(Node):
    @classmethod
    def construct(cls, children):
        node = children.make("BlockableStatementComponent")

        if node is None:
            return None

        children.expecting_line_end()
        return cls(children)
