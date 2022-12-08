from transpiling.statement import Statement
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
        self.transpiler.context.loops += 1
        condition = self.condition.transpile().operate(self.condition, boolean = True)
        statement = Statement(condition.add("while (", ")"))

        if self.label is None:
            self.transpiler.context.loops -= 1
            return statement.append(self.block.transpile()).finish(self, semicolons = False)

        label = self.transpiler.symbols.new_label(self, self.label.string)
        statement.append(self.block.transpile()).drop()

        self.transpiler.context.loops -= 1
        statement = statement if self.label is None else label.surround(statement)
        return statement.finish(self, semicolons = False)
