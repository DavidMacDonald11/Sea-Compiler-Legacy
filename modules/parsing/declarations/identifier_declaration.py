from transpiling.statement import Statement
from .type_keyword import TypeKeyword
from ..node import Node

class IdentifierDeclaration(Node):
    @property
    def nodes(self) -> list:
        return [self.type_keyword, *self.identifiers]

    def __init__(self, type_keyword, arrays, identifiers):
        self.type_keyword = type_keyword
        self.arrays = arrays
        self.identifiers = identifiers

    @classmethod
    def construct(cls):
        type_keyword = TypeKeyword.construct()
        arrays = 0

        while cls.parser.next.has("["):
            cls.parser.take()
            cls.parser.expecting_has("]")
            arrays += 1

        identifiers = [cls.parser.expecting_of("Identifier")]

        while cls.parser.next.has(","):
            cls.parser.take()
            identifiers += [cls.parser.expecting_of("Identifier")]

        return cls(type_keyword, arrays, identifiers)

    def transpile(self):
        kind = self.type_keyword.token.string
        statement = Statement().cast(kind)

        for name in self.identifiers[::-1]:
            identifier = self.transpile_name(name.string, kind)

            if statement.expression.string == "":
                statement.new(f"{identifier}")
            else:
                statement.add(f"{identifier}, ")

        kind = "array" if self.arrays > 0 or kind == "str" else kind
        statement.add(f"__sea_type_{kind}__ ")
        return statement.finish(self)

    def transpile_name(self, name, kind):
        raise NotImplementedError(type(self).__name__)
