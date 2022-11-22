from .line_statement import LineStatement
from .if_statement import IfStatement
from .while_statement import WhileStatement
from .do_while_statement import DoWhileStatement
from .function_statement import FunctionStatement
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
        statement = IfStatement.construct() or WhileStatement.construct()
        statement = statement or DoWhileStatement.construct()
        statement = statement or FunctionStatement.construct()
        statement = statement or LineStatement.construct()

        return cls(statement)

    def transpile(self):
        self.transpiler.write(self.statement.transpile())
