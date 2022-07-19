from ..node import Node

class RangedGenerator(Node):
    @classmethod
    def construct(cls, children):
        if not children.next_token.of("NumericConstant", "CharacterConstant"):
            return None

        children.ignore()

        if children.next_token.has("to"):
            token = children.take_previous()
            children.take()

            if token.specifier == "float":
                token.mark()
                children.warn("Cannot use float in 'to' generator")

            token = children.expecting_of("NumericConstant", "CharacterConstant")

            if token.specifier == "float":
                token.mark()
                children.warn("Cannot use float in 'to' generator")

            return cls(children)

        children.unignore()
        return None
