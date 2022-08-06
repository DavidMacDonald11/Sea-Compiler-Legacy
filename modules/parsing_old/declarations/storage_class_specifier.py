from ..node import Node

class StorageClassSpecifier(Node):
    def construct(self, parser):
        if parser.next.has("register"):
            parser.take()
            return self

        specifier = parser.take() if parser.next.has("external", "static") else None

        if parser.next.has("thread"):
            parser.take()
            parser.expecting_has("local")
            return self

        if parser.next.has("local"):
            parser.take()
            return self

        return None if specifier is None else self
