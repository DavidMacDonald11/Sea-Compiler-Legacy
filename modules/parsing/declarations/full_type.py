from lexing.token import TYPE_MODIFIER_KEYWORDS
from .type_keyword import TypeKeyword
from ..node import Node

class FullType(Node):
    @property
    def nodes(self) -> list:
        nodes = [self.keyword]

        if self.qualifier is not None:
            nodes = [self.qualifier, *nodes]

        return nodes

    def __init__(self, qualifier, keyword, arrays):
        self.qualifier = qualifier
        self.keyword = keyword
        self.arrays = arrays

    @classmethod
    def construct(cls):
        qualifier = cls.parser.take() if cls.parser.next.has(*TYPE_MODIFIER_KEYWORDS) else None
        keyword = TypeKeyword.construct()
        arrays = 0

        while cls.parser.next.has("["):
            cls.parser.take()
            cls.parser.expecting_has("]")
            arrays += 1

        return cls(qualifier, keyword, arrays)

    def transpile(self):
        expression = self.keyword.transpile()
        expression.arrays = self.arrays

        if expression.kind == "str" or self.arrays > 0:
            expression.new("__sea_type_array__")

        return expression
