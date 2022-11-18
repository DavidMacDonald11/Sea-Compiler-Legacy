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
        statement = None
        pairs = self.statement.create_pairs(self.declaration)

        for pair in pairs:
            result = pair.transpile()
            statement = result if statement is None else statement.new(f"%s;\n{result}")

        return statement

    def check_references(self, expression):
        raise NotImplementedError(type(self).__name__)
