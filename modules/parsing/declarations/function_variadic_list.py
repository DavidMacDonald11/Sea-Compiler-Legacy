from ..node import Node

class FunctionVariadicList(Node):
    def construct(self, parser):
        parser.make("TypeName")

        if parser.next.of("Identifier"):
            parser.take()

        variadic = False

        while not variadic and parser.next.has(","):
            parser.take()
            parser.make("TypeName")

            if parser.next.has("*"):
                parser.take()
                variadic = True

            if parser.next.of("Identifier"):
                parser.take()

        return self
