from ..node import Node

class LineStatementComponent(Node):
    @classmethod
    def construct(cls, children):
        if children.next_token_may_be_type:
            children.make("Declaration")
            return cls(children)

        children.make("Expression")

        if not children.next_token.has("\n", "", "while"):
            children.untake()
            children.make("Declaration")

        return cls(children)
