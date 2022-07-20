from ..node import Node

class LineStatement(Node):
    @classmethod
    def construct(cls, children):
        if children.next_token.has("alias"):
            return children.make("AliasStatement")

        if children.next_token.has("assert"):
            return children.make("StaticAssertStatement")

        if children.next_token.has("static"):
            static = children.take()

            if not children.next_token.has("assert"):
                children.untake()
            else:
                children = children.next()
                children += static
                return children.make("StaticAssertStatement", children)

        children.make("LineStatementComponent")
        children.expecting_line_end()

        return cls(children)
