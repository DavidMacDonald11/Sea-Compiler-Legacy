from ..node import Node

class ManageStatement(Node):
    @classmethod
    def construct(cls, children):
        if not children.next_token.has("manage"):
            return None

        children.take()
        children.make("Declaration")
        children.expecting_has(":")
        children.make("BlockStatement", children.next(1))

        return cls(children)
