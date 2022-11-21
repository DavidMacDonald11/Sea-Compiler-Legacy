from .identifier_definition import IdentifierDefinition
from ..declarations.invariable_declaration import InvariableDeclaration

class InvariableDefinition(IdentifierDefinition):
    @classmethod
    def construct(cls):
        declaration = super().construct()

        if isinstance(declaration, InvariableDeclaration):
            cls.parser.warnings.error(declaration, "Cannot declare an invariable without a value")
            cls.parser.expecting_has(r"\n", "EOF")

        return declaration

    @classmethod
    def construct_declaration(cls):
        return InvariableDeclaration.construct()

    def check_references(self, expression):
        owner1 = expression.owners[0]
        owner2 = expression.owners[1]

        if owner1.table_number != owner2.table_number and expression.ownership == "$":
            message = "Cannot transfer ownership into lower-scope identifier"
            self.transpiler.warnings.error(self, message)

        if owner1.ownership == "&" and expression.ownership == "$":
            message = "Cannot take ownership from a borrowed identifier"
            self.transpiler.warnings.error(self, message)
