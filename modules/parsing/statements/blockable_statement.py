from ..node import Node

class BlockableStatement(Node):
    def construct(self, parser):
        if parser.make("BlockableStatementComponent") is None:
            return None

        parser.expecting_line_end()
        return self
