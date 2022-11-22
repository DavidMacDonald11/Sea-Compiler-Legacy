from .line_statement import LineStatementComponent
from .block_statement import BlockStatement, BlockableStatementComponent
from ..expressions.expression import Expression
from ..node import Node

class DoWhileStatement(Node):
    @property
    def nodes(self) -> list:
        if self.label is not None:
            return [self.label, self.block, self.condition]

        return [self.block, self.condition]

    def __init__(self, label, block, condition):
        self.label = label
        self.block = block
        self.condition = condition

    @classmethod
    def construct(cls):
        label = cls.construct_label()

        if label is False:
            return None

        cls.parser.expecting_has(":")

        if cls.parser.next.has(r"\n"):
            block = BlockStatement.construct()
        else:
            block = BlockableStatementComponent.construct() or LineStatementComponent.construct()

            if cls.parser.next.has("while"):
                cls.parser.take()
                condition = Expression.construct()
                cls.parser.expecting_has(r"\n", "EOF")

                return cls(label, block, condition)

        cls.parser.verify_indent()

        if cls.parser.next.has(r"\n"):
            cls.parser.take()

        cls.parser.expecting_has("while")
        condition = Expression.construct()
        cls.parser.expecting_has(r"\n", "EOF")

        return cls(label, block, condition)

    @classmethod
    def construct_label(cls):
        if cls.parser.next.has("do"):
            cls.parser.take()
            label = cls.parser.take() if cls.parser.next.of("Identifier") else None
        elif cls.parser.next.of("Identifier"):
            label = cls.parser.take()

            if not cls.parser.next.has("do"):
                cls.parser.i -= 1
                return False

            cls.parser.take()
        else:
            return False

        return label

    def transpile(self):
        condition = self.condition.transpile().boolean(self.condition)
        statement = condition.new("while(%s);")

        if self.label is None:
            block = self.block.transpile()
            block = block if isinstance(self.block, BlockStatement) else block.new("{ %s; }")
            return statement.new(f"do {block} %s")

        label = self.transpiler.symbols.new_label(self, self.label.string)
        block = self.block.transpile()

        if not isinstance(self.block, BlockStatement):
            block = block.new("{ %s;")
        else:
            block.string = block.string[:-1]

        statement = statement.new("} %s")

        if label is not None:
            statement = label.surround(statement)

        return statement.new(f"do {block} %s")
