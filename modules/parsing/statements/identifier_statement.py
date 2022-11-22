from .variable_definition import VariableDefinition
from .invariable_definition import InvariableDefinition
from ..node import Node

class IdentifierStatement(Node):
    @property
    def nodes(self) -> list:
        return [self.statement]

    def __init__(self, statement):
        self.statement = statement

    def tree_repr(self, prefix):
        return self.statement.tree_repr(prefix)

    @classmethod
    def construct(cls):
        definition = InvariableDefinition if cls.parser.next.has("invar") else VariableDefinition
        statement = definition.construct()

        return cls(statement)

    def transpile(self):
        statement = self.statement.transpile()
        e_type = "/*%e*/" if statement.e_type != "" else ""
        return statement.new(f"%s;{e_type}")
