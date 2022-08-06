from ..node import Node

class SpecifiersAndQualifiers(Node):
    def construct(self, parser):
        specifier = parser.make("StorageClassSpecifier")
        qualifier = parser.make("TypeQualifier")

        return None if (specifier or qualifier) is None else self
