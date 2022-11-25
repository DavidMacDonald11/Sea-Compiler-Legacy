from .type_keyword import TypeKeyword
from ..node import Node

class IdentifierDeclaration(Node):
    @property
    def nodes(self) -> list:
        return [self.type_keyword, *self.identifiers]

    def __init__(self, type_keyword, identifiers):
        self.type_keyword = type_keyword
        self.identifiers = identifiers

    @classmethod
    def construct(cls):
        type_keyword = TypeKeyword.construct()
        identifiers = [cls.parser.expecting_of("Identifier")]

        while cls.parser.next.has(","):
            cls.parser.take()
            identifiers += [cls.parser.expecting_of("Identifier")]

        return cls(type_keyword, identifiers)

    def transpile(self):
        c_type = ""
        decl = ""

        for c_type, identifier in self.transpile_generator():
            decl = f"{identifier}" if decl == "" else f"{identifier}, {decl}"

        return self.transpiler.expression("", f"{self.indent}{c_type} {decl}")

    def transpile_generator(self):
        keyword = self.type_keyword.token.string
        c_type = self.type_keyword.transpile().string

        for name in self.identifiers[::-1]:
            yield (c_type, self.transpile_name(keyword, name.string))

    def transpile_name(self, keyword, name):
        raise NotImplementedError(type(self).__name__)
