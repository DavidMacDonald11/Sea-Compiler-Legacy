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
        sea_keyword =self.declaration.type_keyword.token.string

        if sea_keyword == "bool" and e_type != "bool":
            self.transpiler.warnings.error(self, "Cannot assign non-boolean value to bool variable")

        if sea_keyword not in ("imag32", "imag64", "imag"):
            return (f"/*{e_type}*/", f"{declaration} = {expression}")

        suffix = "f" if sea_keyword == "imag32" else ("l" if sea_keyword == "imag" else "")
        self.transpiler.include("complex")
        return (f"/*{e_type}*/", f"{declaration} = cimag{suffix}({expression})")
