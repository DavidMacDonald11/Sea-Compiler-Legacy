from .identifier_definition import IdentifierDefinition
from ..declarations.variable_declaration import VariableDeclaration

class VariableDefinition(IdentifierDefinition):
    @classmethod
    def construct_declaration(cls):
        return VariableDeclaration.construct()

    def check_references(self, expression):
        if expression.operator == "&":
            message = "Cannot borrow into variables outside of a function call"
            self.transpiler.warnings.error(self, message)

        if expression.invariable:
            verb = "transfer" if expression.operator == "$" else "borrow"
            message = f"Cannot {verb} invariable ownership into variable"
            self.transpiler.warnings.error(self, message)

        super().check_references(expression)
