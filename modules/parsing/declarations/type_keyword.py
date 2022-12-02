from transpiling.expression import Expression
from lexing.token import TYPE_KEYWORDS
from ..node import PrimaryNode

class TypeKeyword(PrimaryNode):
    wrote = []

    @classmethod
    def construct(cls):
        return cls(cls.parser.expecting_has(*TYPE_KEYWORDS))

    def transpile(self):
        kind = self.token.string
        return Expression(kind, f"__sea_type_{kind}__")
