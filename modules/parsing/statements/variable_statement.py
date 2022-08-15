from ..declarations.variable_definition import VariableDefinition
from ..node import Node

class VariableStatement(Node):
    @property
    def nodes(self) -> list:
        return [self.statement]

    def __init__(self, statement):
        self.statement = statement

    @classmethod
    def construct(cls):
        statement = VariableDefinition.construct()
        cls.parser.expecting_has(r"\n", "EOF")
        return cls(statement)

    def transpile(self):
        e_type, statement = self.statement.transpile()
        self.transpiler.write(f"{statement};{e_type}")
