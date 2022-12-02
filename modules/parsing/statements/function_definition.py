from .block_statement import BlockStatement
from ..declarations.function_declaration import FunctionDeclaration
from ..node import Node

class FunctionDefinition(Node):
    @property
    def nodes(self) -> list:
        return [self.declaration, self.block]

    def __init__(self, declaration, block):
        self.declaration = declaration
        self.block = block

    @classmethod
    def construct(cls):
        declaration = FunctionDeclaration.construct()

        if declaration is None:
            return None

        if not cls.parser.next.has(":"):
            cls.parser.expecting_has(r"\n", "EOF")
            return declaration

        cls.parser.take()
        return cls(declaration, BlockStatement.construct())

    def transpile(self):
        statement = self.declaration.transpile_definition(True)
        block = self.block.transpile_for_function()

        function = self.transpiler.context.function

        if function is not None and function.kind != "" and not function.returned:
            self.transpiler.warnings.error(self.declaration, "Function must return a value")

        self.transpiler.context.function = None
        return statement.append(block)
