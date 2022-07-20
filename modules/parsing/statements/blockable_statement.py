from ..node import Node

class BlockableStatement(Node):
    @classmethod
    def construct(cls, children):
        if children.next_token.has("pass"):
            children.take()
            children.expecting_line_end()
            return cls(children)

        if children.next_token.has("continue", "break"):
            children.take()

            if children.next_token.of("Identifier"):
                children.take()

            children.expecting_line_end()
            return cls(children)

        if children.next_token.has("return", "yield"):
            children.take()

            if not children.next_token.has("\n", ""):
                children.make("Expression")

            children.expecting_line_end()
            return cls(children)

        return None
