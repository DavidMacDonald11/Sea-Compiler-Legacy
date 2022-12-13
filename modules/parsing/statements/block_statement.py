from transpiling.statement import Statement
from .line_statement import LineStatement
from .blockable_statement import BlockableStatement
from ..node import Node

class BlockStatement(Node):
    @property
    def nodes(self) -> list:
        return self.statements

    def __init__(self, statements):
        self.statements = statements

    @classmethod
    def construct(cls):
        if not cls.parser.next.has(r"\n"):
            statement = BlockableStatement.construct() or LineStatement.construct()

            if isinstance(statement, cls.parser.statement):
                statement = statement.statement

            return cls([statement])

        cls.parser.take()
        cls.parser.indents += 1

        empty = True
        exited = False
        statements = []

        while cls.parser.next.depth >= cls.parser.indents:
            cls.parser.verify_indent()
            if cls.parser.next.has(r"\n", "EOF"): continue

            empty = False
            statement = BlockableStatement.construct()
            statement = statement or cls.parser.statement.construct().statement
            statements += [statement]

            if exited:
                message = "Unreachable code following a block exit or pass keyword"
                cls.parser.warnings.warn(statements[-1], message)

            exited = isinstance(statements[-1], BlockableStatement)

        if empty:
            message = "Block cannot be empty; use the pass keyword"
            cls.parser.warnings.error(cls.parser.take(), message)

        cls.parser.indents -= 1
        return cls(statements)

    def transpile(self):
        self.transpiler.push_symbol_table()
        return self.transpile_without_symbol_table()

    def transpile_without_symbol_table(self):
        self.transpiler.context.blocks += 1
        block = Statement().new("{").append()

        for statement in self.statements:
            block.new_append(statement.transpile())

        block.drop().append(self.transpiler.symbols.free().drop().finish(self))
        self.transpiler.pop_symbol_table()
        self.transpiler.context.blocks -= 1

        return block.new("}")
