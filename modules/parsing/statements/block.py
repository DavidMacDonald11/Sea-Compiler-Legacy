from ..node import Node

class Block(Node):
    @classmethod
    def construct(cls, children):
        if not children.next_token.has("block"):
            return None

        children.take()
        children.expecting_has(":")
        children.make("BlockStatement", children.next(1))

        return cls(children)
