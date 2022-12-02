from transpiling.statement import Statement
from .line_statement import LineStatementComponent
from .blockable_statement import BlockableStatementComponent
from .block_statement import BlockStatement
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
        self.transpiler.context.loops += 1
        condition = self.condition.transpile().operate(self.condition, boolean = True)
        condition.add("while(", ");")
        statement = Statement()

        if self.label is None:
            block = self.block.transpile()

            if not isinstance(self.block, BlockStatement):
                block.finish(self).add("\t")
                statement.new("do {").append(block).new("}")
                return statement.append(Statement(condition)).finish(self, semicolons = False)

            statement.new("do").append(block).new_append(Statement(condition))
            return statement.finish(self, semicolons = False)

        label = self.transpiler.symbols.new_label(self, self.label.string)
        block = self.block.transpile()

        if not isinstance(self.block, BlockStatement):
            block.finish(self).add("\t")
            statement.new("do {").append(block).new("}")
        else:
            statement.new("do").append(block)
            statement.lines = statement.lines[:-1]

        if label is not None:
            label = label.surround(Statement().new(condition.add("} ")))
            statement.new("").new_append(label).drop()

        self.transpiler.context.loops -= 1
        return statement.finish(self, semicolons = False)
