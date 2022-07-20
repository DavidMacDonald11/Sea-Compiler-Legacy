from ..node import Node

class StorageClassSpecifier(Node):
    @classmethod
    def construct(cls, children):
        if children.next_token.has("register"):
            children.take()
            return cls(children)

        specifier = None

        if children.next_token.has("external", "static"):
            specifier = children.take()

        if children.next_token.has("thread"):
            children.take()
            children.expecting_has("local")
            return cls(children)

        if children.next_token.has("local"):
            children.take()
            return cls(children)

        return None if specifier is None else cls(children)
