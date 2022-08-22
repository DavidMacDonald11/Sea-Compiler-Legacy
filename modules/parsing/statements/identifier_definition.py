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
        statement = self.statement.transpile()
        c_type = ""
        decl = ""

        for c_type, identifier in self.declaration.transpile_generator():
            expression = identifier.assign(self, statement)
            is_ref = expression.is_reference

            delcaration = f"{'*' if is_ref else ''}{identifier}"
            decl = delcaration if decl == "" else f"{delcaration}, {decl}"

        decl = f"{c_type} {decl}"

        if is_ref:
            self.check_references(not expression.is_invar)

        return statement.new(f"{decl} = %s")

    def check_references(self, is_var):
        raise NotImplementedError(type(self).__name__)
