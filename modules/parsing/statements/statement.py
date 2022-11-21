from .line_statement import LineStatement
from .if_statement import IfStatement
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
        statement = IfStatement.construct() or LineStatement.construct()
        return cls(statement)

    def transpile(self):
        statement = self.statement.transpile()
        self.transpiler.write(statement)
