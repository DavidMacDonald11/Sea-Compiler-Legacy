from ..node import Node

class BlockableStatementComponent(Node):
    @classmethod
    def construct(cls, children):
        if children.next_token.has("pass"):
            children.take()
            return cls(children)

        if children.next_token.has("continue", "break"):
            children.take()

            if children.next_token.of("Identifier"):
                children.take()

            return cls(children)

        if children.next_token.has("return", "yield"):
            children.take()

            if not children.next_token.has("\n", ""):
                children.make("Expression")

            return cls(children)

        return None
