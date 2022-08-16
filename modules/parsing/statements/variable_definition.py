from ..declarations.variable_declaration import VariableDeclaration
from ..statements.assignment_statement import AssignmentStatement
from ..node import Node

class VariableDefinition(Node):
    @property
    def nodes(self) -> list:
        return [self.declaration, self.statement]

    def __init__(self, declaration, statement):
        self.declaration = declaration
        self.statement = statement

    @classmethod
    def construct(cls):
        declaration = VariableDeclaration.construct()

        if not cls.parser.next.has("="):
            return declaration

        cls.parser.take()
        return cls(declaration, AssignmentStatement.construct())

    def transpile(self):
        _, declaration = self.declaration.transpile()
        e_type, statement = self.statement.transpile()
        var = self.transpiler.symbols[self.declaration.identifiers[0].string]

        return var.assign(self, e_type, statement, declaration)
