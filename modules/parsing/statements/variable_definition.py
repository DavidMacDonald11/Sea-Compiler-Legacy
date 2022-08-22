from .identifier_definition import IdentifierDefinition
from ..declarations.variable_declaration import VariableDeclaration

class VariableDefinition(IdentifierDefinition):
    @classmethod
    def construct_declaration(cls):
        return VariableDeclaration.construct()

    def check_references(self, expression):
        if expression.ownership == "&":
            message = "Cannot borrow into variables outside of a function call"
            self.transpiler.warnings.error(self, message)

        if len(self.declaration.identifiers) > 1 and expression.ownership == "$":
            message = "Cannot transfer ownership to multiple identifiers"
            self.transpiler.warnings.error(self, message)

        if expression.is_invar:
            verb = "transfer" if expression.ownership == "$" else "borrow"
            message = f"Cannot {verb} invariable ownership into variable"
            self.transpiler.warnings.error(self, message)
