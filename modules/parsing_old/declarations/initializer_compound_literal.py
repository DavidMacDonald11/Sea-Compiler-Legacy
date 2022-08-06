from ..node import Node

class InitializerCompoundLiteral(Node):
    def construct(self, parser):
        lbracket = parser.expecting_has("{", "[")
        rbracket = "]" if lbracket.has("[") else "}"
        self.construct_initializer_list(parser, rbracket)
        parser.expecting_has(rbracket)

        return self

    def construct_initializer_list(self, parser, rbracket):
        node = parser.make("RangedGenerator")
        node = node or parser.make("IterativeGenerator")

        if node is not None:
            return

        self.ignore_format_tokens(parser)
        parser.make("DesignatedInitializer")

        while parser.next.has(","):
            parser.take()
            self.ignore_format_tokens(parser)

            if parser.next.has(rbracket):
                return

            parser.make("DesignatedInitailizer")

        self.ignore_format_tokens(parser)

    def ignore_format_tokens(self, parser):
        while parser.next.has("\n", "\t", " " * 4) or parser.next.of("Annotation"):
            if parser.next.of("Annotation"):
                parser.ignore()
            else:
                parser.take()
