from .variable_definition import VariableDefinition
from ..declarations.variable_declaration import VariableDeclaration
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

        if isinstance(statement, VariableDeclaration):
            cls.parser.expecting_has(r"\n", "EOF")

        return cls(statement)

    def transpile(self):
        e_type, statement = self.statement.transpile()
        e_type = f"/*{e_type}*/" if e_type != "" else ""
        self.transpiler.write(f"{statement}{e_type};")
