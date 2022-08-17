from .assignment_statement import AssignmentStatement
from ..node import Node

class IdentifierDefinition(Node):
    @property
    def nodes(self) -> list:
        return [self.declaration, self.statement]

    def __init__(self, declaration, statement):
        self.declaration = declaration
        self.statement = statement

    @classmethod
    def construct(cls):
        declaration = cls.construct_declaration()

        if not cls.parser.next.has("="):
            return declaration

        cls.parser.take()
        return cls(declaration, AssignmentStatement.construct())

    @classmethod
    def construct_declaration(cls):
        raise NotImplementedError()

    def transpile(self):
        _, declaration = self.declaration.transpile()
        e_type, statement = self.statement.transpile()
        var = self.transpiler.symbols[self.declaration.identifiers[0].string]

        return var.assign(self, e_type, statement, declaration)
