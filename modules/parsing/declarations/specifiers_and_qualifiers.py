from ..node import Node

class SpecifiersAndQualifiers(Node):
    @classmethod
    def construct(cls, children):
        specifier = children.make("StorageClassSpecifier")
        qualifier = children.make("TypeQualifier")

        return None if (specifier or qualifier) is None else cls(children)
