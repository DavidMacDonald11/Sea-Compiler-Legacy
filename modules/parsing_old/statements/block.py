from ..node import Node

class Block(Node):
    def construct(self, parser):
        if not parser.next.has("block"):
            return None

        parser.take()
        parser.expecting_has(":")
        parser.make("BlockStatement", depth = 1)

        return self
