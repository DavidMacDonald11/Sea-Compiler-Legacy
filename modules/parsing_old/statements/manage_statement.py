from ..node import Node

class ManageStatement(Node):
    def construct(self, parser):
        if not parser.next.has("manage"):
            return None

        parser.take()
        parser.make("Declaration")
        parser.expecting(":")
        parser.make("BlockStatement", depth = 1)

        return self
