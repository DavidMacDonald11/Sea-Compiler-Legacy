from ..node import Node

class TypeQualifier(Node):
    def construct(self, parser):
        if not parser.next.has("atomic", "const", "restrict", "volatile"):
            return None

        parser.take()
        parser.make("TypeQualifier", parser)
        return self
