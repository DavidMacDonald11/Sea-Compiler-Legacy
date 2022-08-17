from lexing.token import TYPE_KEYWORDS, TYPE_MODIFIER_KEYWORDS
from .expression_statement import ExpressionStatement
from .identifier_statement import IdentifierStatement
from .compound_assignment_statement import CompoundAssignmentStatement
from ..node import Node

class Statement(Node):
    @property
    def nodes(self) -> list:
        return [self.statement]

    def __init__(self, statement):
        self.statement = statement

    def tree_repr(self, prefix):
        return self.statement.tree_repr(prefix)

    @classmethod
    def construct(cls):
        if cls.parser.next.has(*TYPE_MODIFIER_KEYWORDS, *TYPE_KEYWORDS):
            return IdentifierStatement.construct()

        if cls.parser.next.of("Identifier"):
            return cls(CompoundAssignmentStatement.construct())

        return cls(ExpressionStatement.construct())

    def transpile(self):
        e_type, statement = self.statement.transpile()
        self.transpiler.write(f"{statement}/*{e_type}*/;")
