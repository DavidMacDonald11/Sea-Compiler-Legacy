from ..node import Node

class AliasStatement(Node):
    @classmethod
    def construct(cls, children):
        children.take()

        if children.next_token.has("type"):
            children.take()
            children.expecting_has("of")
            children.make("Expression")
        else:
            children.make("TypeName")

        children.expecting_has("as")
        children.expecting_of("Identifier")

        children.take_comments()
        children.expecting_has("\n", "")
        children.ignore_format_tokens()

        return cls(children)
