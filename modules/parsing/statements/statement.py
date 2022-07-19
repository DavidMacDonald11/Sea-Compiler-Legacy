from ..node import Node

class Statement(Node):
    @classmethod
    def construct(cls, children):
        skip_newlines(children)

        if children.next_token.has("alias"):
            return cls.construct_alias(children)

        if children.next_token_may_be_type:
            children.make("Declaration")
        else:
            children.make("Expression")

            if not children.next_token.has("\n"):
                children.unignore()
                children.nodes = children.nodes[:-1]
                children.make("Declaration")

        take_comments(children)
        children.expecting_has("\n")
        skip_newlines(children)

        return cls(children)

    @classmethod
    def construct_alias(cls, children):
        children.take()

        if children.next_token.has("type"):
            children.take()
            children.expecting_has("of")
            children.make("Expression")
        else:
            children.make("TypeName")

        children.expecting_has("as")
        children.expecting_of("Identifier")

        take_comments(children)
        children.expecting_has("\n")
        skip_newlines(children)

        return cls(children, "alias")

def skip_newlines(children):
    while children.next_token.has("\n") or children.next_token.of("Annotation"):
        if children.next_token.has("\n"):
            children.ignore()
        else:
            children.take()

def take_comments(children):
    while children.next_token.of("Annotation"):
        children.take()
