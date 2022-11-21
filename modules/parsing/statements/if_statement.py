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

        if cls.check_indent() is False:
            return cls(condition, block, [])

        elses = []
        else_if = True

        while else_if and cls.parser.next.has("else"):
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

            if cls.check_indent() is False: break

        return cls(condition, block, elses)

    @classmethod
    def check_indent(cls):
        return False if cls.parser.next.depth < cls.parser.indents else cls.parser.verify_indent()

    def transpile(self):
        condition = self.condition.transpile().boolean(self.condition)
        block = self.block.transpile()
        statement = self.transpiler.expression("", f"if ({condition}) {block}")

        for else_if in self.elses:
            statement = statement.new(f"%s else {else_if.transpile()}")

        return statement

class ElseIfStatement(IfStatement):
    pass

class ElseStatement(IfStatement):
    @property
    def nodes(self) -> list:
        return [self.block]

    def transpile(self):
        return self.block.transpile()
