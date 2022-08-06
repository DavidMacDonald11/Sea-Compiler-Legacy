from ..node import Node

class TemplateDeclaration(Node):
    def construct(self, parser):
        if not parser.next.has("template"):
            return None

        parser.take()
        parser.expecting_has("with")

        empty = True

        while parser.next.has("type"):
            empty = False
            parser.expecting_has("type")
            parser.expecting_of("Identifier")

            if parser.next.has(","):
                parser.take()

        parser.expecting_line_end()

        if empty:
            self.mark()
            parser.warn("Cannot have empty template")

        return self
