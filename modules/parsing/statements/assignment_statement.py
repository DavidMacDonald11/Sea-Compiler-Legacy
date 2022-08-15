from .expression_statement import ExpressionStatement
from ..node import Node

class AssignmentStatement(Node):
    @property
    def nodes(self) -> list:
        return [self.identifier, self.expression]

    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression

    @classmethod
    def construct(cls):
        identifier = cls.parser.take()

        if not cls.parser.next.has("="):
            cls.parser.i -= 1
            return ExpressionStatement.construct()

        cls.parser.take()
        return cls(identifier, cls.construct())

    def transpile(self):
        name = self.identifier.string
        var = self.transpiler.symbols[name]
        e_type, expression = self.expression.transpile()

        if var is None:
            self.transpiler.warnings.error(self, f"Assigning undeclared variable '{name}'")
            return (e_type, f"/*{name} = */{expression}")

        return var.assign(self, e_type, expression)
