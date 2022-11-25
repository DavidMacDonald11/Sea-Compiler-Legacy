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

        if expression.is_invar:
            verb = "transfer" if expression.ownership == "$" else "borrow"
            message = f"Cannot {verb} invariable ownership into variable"
            self.transpiler.warnings.error(self, message)

        owner1 = expression.owners[0]
        owner2 = expression.owners[1]

        if None in (owner1, owner2):
            return

        if owner1.table_number != owner2.table_number:
            message = "Cannot transfer ownership into lower-scope identifier"
            self.transpiler.warnings.error(self, message)

        if owner1.ownership == "&" and expression.ownership == "$":
            message = "Cannot take ownership from a borrowed identifier"
            self.transpiler.warnings.error(self, message)
