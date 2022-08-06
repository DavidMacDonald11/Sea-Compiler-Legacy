from ..node import Node

class AliasStatement(Node):
    def construct(self, parser):
        parser.take()

        if parser.next.has("type"):
            parser.take()
            parser.expecting_has("of")
            parser.make("Expression")
        else:
            parser.make("TypeName")

        parser.expecting_has("as")
        parser.expecting_of("Identifier")
        parser.expecting_line_end()

        return self
