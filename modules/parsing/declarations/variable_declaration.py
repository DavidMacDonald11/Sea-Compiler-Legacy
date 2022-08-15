from .type_keyword import TypeKeyword
from ..node import Node

class VariableDeclaration(Node):
    @property
    def nodes(self) -> list:
        return [self.type_keyword, *self.identifiers]

    def __init__(self, type_keyword, identifiers):
        self.type_keyword = type_keyword
        self.identifiers = identifiers

    @classmethod
    def construct(cls):
        type_keyword = TypeKeyword.construct()
        identifiers = []

        identifiers += [cls.parser.expecting_of("Identifier")]

        while cls.parser.next.has(","):
            cls.parser.take()
            identifiers += [cls.parser.expecting_of("Identifier")]

        return cls(type_keyword, identifiers)

    def transpile(self):
        sea_keyword = self.type_keyword.token.string
        _, keyword = self.type_keyword.transpile()
        identifiers = ""

        for identifier in self.identifiers:
            name = self.transpiler.symbols.new_variable(sea_keyword, identifier.string)

            if name is None:
                self.transpiler.error(self, f"Cannot declare variable {identifier} twice.")
                return f"{keyword} {identifiers}/*, {identifier}*/"

            identifiers = name if identifiers == "" else f"{identifiers}, {name}"

        return "", f"{keyword} {identifiers}"
