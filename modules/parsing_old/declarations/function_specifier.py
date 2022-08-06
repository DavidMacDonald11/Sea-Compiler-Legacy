from ..node import Node

class FunctionSpecifier(Node):
    def construct(self, parser):
        parser.make("StorageClassSpecifier")

        if parser.next.has("inline"):
            parser.take()

            if parser.next.has("deviant"):
                parser.take()

            return self

        if parser.next.has("deviant"):
            parser.take()

        if parser.next.has("inline"):
            parser.take()

        return None if len(parser.children) == 0 else self
