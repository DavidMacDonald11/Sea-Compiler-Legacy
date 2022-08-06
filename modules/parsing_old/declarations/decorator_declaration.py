from ..node import Node

class DecoratorDeclaration(Node):
    def construct(self, parser):
        if not parser.next.has("decorate"):
            return None

        parser.take()
        parser.expecting_has("with")

        empty = True

        while parser.next.of("Identifier"):
            empty = False
            parser.take()
            parser.make("CallOperator")

            if parser.next.has(","):
                parser.take()

        parser.expecting_line_end()

        if empty:
            self.mark()
            parser.warn("Cannot have empty decorator")

        return self
