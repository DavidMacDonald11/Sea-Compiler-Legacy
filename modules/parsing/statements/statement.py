from ..node import Node

class Statement(Node):
    @classmethod
    def construct(cls, children):
        children.make("Expression")
        children.expecting_has("\n")
        return cls(children)
