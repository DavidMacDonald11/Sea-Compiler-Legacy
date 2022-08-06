from ..node import Node

class BlockableStatementComponent(Node):
    def construct(self, parser):
        if parser.next.has("pass"):
            parser.take()
            return self

        if parser.next.has("continue", "break"):
            parser.take()

            if parser.next.of("Identifier"):
                parser.take()

            return self

        if not parser.next.has("return", "yield"):
            return None

        parser.take()

        if not parser.next.has("\n", ""):
            parser.make("Expression")

        return self
