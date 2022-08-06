from ..node import Node

class RangedGenerator(Node):
    def construct(self, parser):
        if not parser.next.of("NumericConstant", "CharacterConstant"):
            return None

        parser.ignore()

        if not parser.next.has("to"):
            parser.unignore()
            return None

        token = parser.take_previous()
        parser.take()

        if token.specifier == "float":
            token.mark()
            parser.warn("Cannot use float in 'to' generator")

        token = parser.expecting_of("NumericConstant", "CharacterConstant")

        if parser.specifier == "float":
            token.mark()
            parser.warn("Cannot use float in 'to' generator")

        return self
