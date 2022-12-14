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
        owner1 = expression.owners[0]
        owner2 = expression.owners[1]

        if None in (owner1, owner2):
            return

        if owner1.kind != owner2.kind:
            message = f"Ownership must be passed to exact same type ({owner1.kind})"
            self.transpiler.warnings.error(self, message)

        if owner1.table_number != owner2.table_number:
            message = "Cannot transfer ownership into lower-scope identifier"
            self.transpiler.warnings.error(self, message)

        if owner1.ownership == "&" and expression.operator == "$":
            message = "Cannot take ownership from a borrowed identifier"
            self.transpiler.warnings.error(self, message)

        owner2.fun_local = owner1.fun_local
        owner2.heap = owner1.heap
