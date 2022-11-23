from .block_statement import BlockStatement
from ..expressions.expression import Expression
from ..node import Node

class WhileStatement(Node):
    @property
    def nodes(self) -> list:
        if self.label is not None:
            return [self.label, self.condition, self.block]

        return [self.condition, self.block]

    def __init__(self, label, condition, block):
        self.label = label
        self.condition = condition
        self.block = block

    @classmethod
    def construct(cls):
        if cls.parser.next.has("while"):
            label = None
        elif cls.parser.next.of("Identifier"):
            label = cls.parser.take()

            if not cls.parser.next.has("while"):
                cls.parser.i -= 1
                return None
        else:
            return None

        cls.parser.take()
        condition = Expression.construct()
        cls.parser.expecting_has(":")
        block = BlockStatement.construct()

        return cls(label, condition, block)

    def transpile(self):
        condition = self.condition.transpile().boolean(self.condition)
        statement = condition.new("while (%s)")

        if self.label is None:
            return statement.new(f"{self.indent}%s {self.block.transpile()}")

        label = self.transpiler.symbols.new_label(self, self.label.string)
        statement = statement.new(f"{self.indent}%s {self.block.transpile()}")

        return statement if self.label is None else label.surround(self, statement)
