from ..node import Node

class DesignatedInitializer(Node):
    def construct(self, parser):
        if not parser.next.has("["):
            parser.make("Initializer")

            if parser.next.has(":"):
                parser.take()
                parser.make("Initializer")

            return self

        parser.take()

        if parser.make("RangedGenerator") is None:
            parser.make("ConstantExpression")

        parser.expecting_has("]")
        parser.expecting_has(":")
        parser.make("Initializer")

        return self
