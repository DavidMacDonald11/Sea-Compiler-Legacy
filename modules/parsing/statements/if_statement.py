from .block_statement import BlockStatement
from ..expressions.expression import Expression
from ..node import Node

class IfStatement(Node):
    @property
    def nodes(self) -> list:
        return [self.condition, self.block, *self.elses]

    def __init__(self, condition, block, elses):
        self.condition = condition
        self.block = block
        self.elses = elses

    @classmethod
    def construct(cls):
        if not cls.parser.next.has("if"):
            return None

        cls.parser.take()
        condition = Expression.construct()
        cls.parser.expecting_has(":")
        block = BlockStatement.construct()

        if cls.parser.next.depth < cls.parser.indents:
            return cls(condition, block, [])

        indent = cls.parser.verify_indent()

        elses = []
        else_if = True

        while else_if and cls.parser.next.has("else"):
            indent = None
            elif_condition = None
            cls.parser.take()

            if cls.parser.next.has("if"):
                cls.parser.take()
                elif_condition = Expression.construct()
            else:
                else_if = False

            cls.parser.expecting_has(":")

            kind = ElseIfStatement if else_if else ElseStatement
            elses += [kind(elif_condition, BlockStatement.construct(), [])]

            if cls.parser.next.depth < cls.parser.indents: break
            indent = cls.parser.verify_indent()

        if indent is not None:
            cls.parser.i -= 1

        return cls(condition, block, elses)

    def transpile(self):
        condition = self.condition.transpile().boolean(self.condition)
        block = self.block.transpile()
        statement = self.transpiler.expression("", f"if ({condition}) {block}")

        for i, else_if in enumerate(self.elses):
            if i != 0: statement.new(f"{self.indent}%s")
            statement.new(f"%s {self.indent}else {else_if.transpile()}")

        return statement

class ElseIfStatement(IfStatement):
    pass

class ElseStatement(IfStatement):
    @property
    def nodes(self) -> list:
        return [self.block]

    def transpile(self):
        return self.block.transpile()
