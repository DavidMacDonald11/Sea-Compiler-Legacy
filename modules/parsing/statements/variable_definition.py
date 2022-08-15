from ..declarations.variable_declaration import VariableDeclaration
from ..statements.expression_statement import ExpressionStatement
from ..node import Node

class VariableDefinition(Node):
    @property
    def nodes(self) -> list:
        return [self.declaration, self.expression]

    def __init__(self, declaration, expression):
        self.declaration = declaration
        self.expression = expression

    @classmethod
    def construct(cls):
        declaration = VariableDeclaration.construct()

        if not cls.parser.next.has("="):
            return declaration

        cls.parser.take()
        return cls(declaration, ExpressionStatement.construct())

    def transpile(self):
        _, declaration = self.declaration.transpile()
        e_type, expression = self.expression.transpile()
        var = self.transpiler.symbols[self.declaration.identifiers[0].string]

        return var.assign(self, e_type, expression, declaration)
