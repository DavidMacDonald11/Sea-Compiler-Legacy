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
        identifier = self.transpiler.symbols.at(self, name)
        expression = self.expression.transpile()

        if expression.ownership is not None:
            self.transpiler.warnings.error(self, "Must create new identifier to transfer ownership")

        if identifier is None:
            return expression.new(f"/*{name} = */%s")

        return identifier.assign(self, expression).new(f"{identifier} = %s")
