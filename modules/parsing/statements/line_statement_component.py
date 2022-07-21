from ..node import Node

class LineStatementComponent(Node):
    def construct(self, parser):
        if parser.next.may_be_type():
            parser.make("Declaration")
            return self

        parser.make("Expression")

        if not parser.next.has("\n", "", "while"):
            parser.untake()
            parser.make("Declaration")

        return self
