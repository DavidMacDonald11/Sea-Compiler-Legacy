from ..node import Node

class FileStatement(Node):
    @classmethod
    def construct(cls, children):
        return cls(children)
