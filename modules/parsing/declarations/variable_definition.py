from .variable_declaration import VariableDeclaration
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
        return cls(declaration, cls.parser.expression.construct())

    def transpile(self):
        _, declaration = self.declaration.transpile()
        e_type, expression = self.expression.transpile()
        return f"/*{e_type}*/", f"{declaration} = {expression}"
