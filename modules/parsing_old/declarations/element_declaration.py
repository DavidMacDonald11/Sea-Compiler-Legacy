from ..node import Node

class ElementDeclaration(Node):
    def construct(self, parser):
        parser.make("TypeName")
        parser.expecting_of("Identifier")

        while parser.next.has(","):
            parser.take()

            if parser.next.of("Identifier"):
                parser.take()

                if parser.next.of("Identifier"):
                    parser.take()
            else:
                parser.make("TypeName")
                parser.expecting_of("Identifier")

        return self
