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
        pass
