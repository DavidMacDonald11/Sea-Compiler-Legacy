from ..node import Node

class SpecifiersAndQualifiers(Node):
    @classmethod
    def construct(cls, children):
        if children.next_token.has("register"):
            children.take()
            children.make("TypeQualifier")
            return cls(children)

        specifier = None

        if children.next_token.has("external", "static"):
            specifier = children.take()

        if children.next_token.has("thread"):
            children.take()
            children.expecting_has("local")
            children.make("TypeQualifier")
            return cls(children)

        if children.next_token.has("local"):
            children.take()
            children.make("TypeQualifier")
            return cls(children)

        qualifier = children.make("TypeQualifier")
        specifier = specifier or qualifier

        return None if specifier is None else cls(children)
