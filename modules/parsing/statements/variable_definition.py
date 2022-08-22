from .identifier_definition import IdentifierDefinition
from ..declarations.variable_declaration import VariableDeclaration

class VariableDefinition(IdentifierDefinition):
    @classmethod
    def construct_declaration(cls):
        return VariableDeclaration.construct()

    def check_references(self, is_var):
        if len(self.declaration.identifiers) > 1 and is_var:
            self.transpiler.warnings.error(self, "Cannot create multiple references to variable")

        if not is_var:
            self.transpiler.warnings.error(self, "Cannot create variable reference to invariable")
