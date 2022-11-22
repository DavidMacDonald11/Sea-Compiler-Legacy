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
            statement = BlockableStatement.construct() or LineStatement.construct()

            if isinstance(statement, cls.parser.statement):
                statement = statement.statement

            return cls([statement], cls.parser.indents)

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
                message = "Cannot have unreacahble code following a block exit or pass keyword"
                cls.parser.warnings.warn(statements[-1], message)

            exited = isinstance(statements[-1], (PassStatement, BreakContinueStatement))

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

class BlockableStatement(Node):
    @classmethod
    def construct(cls):
        statement = BlockableStatementComponent.construct()
        cls.parser.expecting_has(r"\n", "EOF")
        return statement

class BlockableStatementComponent(Node):
    @classmethod
    def construct(cls):
        return PassStatement.construct() or BreakContinueStatement.construct()

class PassStatement(PrimaryNode):
    @classmethod
    def construct(cls):
        return cls(cls.parser.take()) if cls.parser.next.has("pass") else None

    def transpile(self):
        return self.transpiler.expression("", "/*pass*/")

class BreakContinueStatement(Node):
    @property
    def nodes(self) -> list:
        return [self.keyword] if self.label is None else [self.keyword, self.label]

    def __init__(self, keyword, label):
        self.keyword = keyword
        self.label = label

    @classmethod
    def construct(cls):
        if not cls.parser.next.has("break", "continue"):
            return None

        keyword = cls.parser.take()
        label = cls.parser.take() if cls.parser.next.of("Identifier") else None

        return cls(keyword, label)

    def transpile(self):
        statement = self.transpiler.expression()

        if self.label is None:
            return statement.new(self.keyword.string)

        label = self.transpiler.symbols.at(self, self.label.string)

        if label is None:
            return statement.new(f"/*{self.keyword.string} {self.label.string}*/")

        return statement.new(f"goto {label.c_name}_{self.keyword.string}__")
