from ..node import Node

class Statement(Node):
    @classmethod
    def construct(cls, children):
        skip_newlines(children)

        children.make("Expression")
        children.expecting_has("\n")

        skip_newlines(children)

        return cls(children)

def skip_newlines(children):
    while children.next_token.has("\n"):
        children.ignore()
