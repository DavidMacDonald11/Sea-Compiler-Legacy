from ..node import Node

class TypeQualifier(Node):
    @classmethod
    def construct(cls, children):
        if children.next_token.has("atomic", "const", "restrict", "volatile"):
            children.take()
            children.make("TypeQualifier", children)
            return cls(children)

        return None
