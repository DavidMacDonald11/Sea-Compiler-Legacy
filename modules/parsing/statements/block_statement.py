from .line_statement import LineStatement
from ..node import Node, PrimaryNode

class BlockStatement(Node):
    @property
    def nodes(self) -> list:
        return self.statements

    def __init__(self, statements, indents):
        self.statements = statements
        self.indents = indents

    @classmethod
    def construct(cls):
        if not cls.parser.next.has(r"\n"):
            statements = [BlockableStatement.construct() or LineStatement.construct()]
            return cls(statements, cls.parser.indents)

        cls.parser.take()
        cls.parser.indents += 1

        empty = True
        passed = False
        statements = []

        while cls.parser.next.depth >= cls.parser.indents:
            cls.parser.verify_indent()
            if cls.parser.next.has(r"\n", "EOF"): continue

            empty = False
            statement = BlockableStatement.construct()
            statement = statement or cls.parser.statement.construct().statement
            statements += [statement]

            if passed:
                message = "Cannot have code following the pass keyword in a block"
                cls.parser.warnings.warn(statements[-1], message)

            passed = isinstance(statements[-1], PassStatement)

        if empty:
            message = "Block cannot be empty; use the pass keyword"
            cls.parser.warnings.warn(cls.parser.take(), message)

        cls.parser.indents -= 1
        return cls(statements, cls.parser.indents + 1)

    def transpile(self):
        self.transpiler.push_symbol_table()

        indents = "\t" * (self.indents - 1)
        block = self.statements[0].transpile().new(f"{{\n\t{indents}%s")

        for statement in self.statements[1:]:
            block = block.new(f"%s;\n\t{indents}{statement.transpile()}")

        self.transpiler.pop_symbol_table()
        return block.new(f"%s;\n{indents}}}")

# TODO consider conditional ownership changes
# TODO maybe no ownership changes in lower scopes

class BlockableStatement(Node):
    @classmethod
    def construct(cls):
        if cls.parser.next.has("pass"):
            keyword = cls.parser.take()
            cls.parser.expecting_has(r"\n", "EOF")

            return PassStatement(keyword)

        return None

class PassStatement(PrimaryNode):
    def transpile(self):
        return self.transpiler.expression("", "/*pass*/")
