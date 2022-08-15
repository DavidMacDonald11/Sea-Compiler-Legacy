from lexing.token import TYPE_KEYWORDS
from .expression_statement import ExpressionStatement
from .variable_statement import VariableStatement
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
        if cls.parser.next.has(*TYPE_KEYWORDS):
            return VariableStatement.construct()

        if cls.parser.next.of("Identifier"):
            return cls(CompoundAssignmentStatement.construct())

        return cls(ExpressionStatement.construct())

    def transpile(self):
        e_type, statement = self.statement.transpile()
        self.transpiler.write(f"{statement}/*{e_type}*/;")
