from ..node import Node

class Statement(Node):
    @classmethod
    def construct(cls, children):
        skip_newlines(children)

        children.make("Expression")
        take_comments(children)
        children.expecting_has("\n")

        skip_newlines(children)

        return cls(children)

def skip_newlines(children):
    nextt = children.next_token

    while nextt.has("\n") or nextt.of("Annotation"):
        if nextt.has("\n"):
            children.ignore()
        else:
            children.take()

        nextt = children.next_token

def take_comments(children):
    while children.next_token.of("Annotation"):
        children.take()
