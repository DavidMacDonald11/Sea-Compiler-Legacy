from .function_definition import FunctionDefinition
from ..node import Node

class FunctionStatement(Node):
    @property
    def nodes(self) -> list:
        return [self.statement]

    def __init__(self, statement):
        self.statement = statement

    def tree_repr(self, prefix):
        return self.statement.tree_repr(prefix)

    @classmethod
    def construct(cls):
        statement = FunctionDefinition.construct()
        return None if statement is None else cls(statement)

    def transpile(self):
        return self.statement.transpile()
