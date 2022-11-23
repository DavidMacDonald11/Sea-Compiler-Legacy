from .assignment_statement import AssignmentStatement, AssignmentList
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
        return AssignmentList.transpile_lists(self.statement.make_lists(self, self.declaration))

    def check_references(self, expression):
        raise NotImplementedError(type(self).__name__)
