from .line_statement import LineStatement
from ..expressions.expression import Expression
from ..node import Node, PrimaryNode

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
                message = "Cannot have unreacahble code following a block exit or pass keyword"
                cls.parser.warnings.warn(statements[-1], message)

            exited = isinstance(statements[-1], BlockableStatement)

        if empty:
            message = "Block cannot be empty; use the pass keyword"
            cls.parser.warnings.warn(cls.parser.take(), message)

        cls.parser.indents -= 1
        return cls(statements)

    def transpile(self):
        self.transpiler.push_symbol_table()
        return self.transpile_for_function()

    def transpile_for_function(self):
        self.transpiler.indents += 1
        block = self.statements[0].transpile().new(f"\n{self.indent[:-1]}{{\n%s")

        for statement in self.statements[1:]:
            block = block.new(f"%s;\n{statement.transpile()}")

        self.transpiler.pop_symbol_table()
        self.transpiler.indents -= 1

        return block.new(f"%s;\n{self.indent}}}")

class BlockableStatement(Node):
    @property
    def nodes(self) -> list:
        return [self.statement]

    def __init__(self, statement):
        self.statement = statement

    def tree_repr(self, prefix):
        return self.statement.tree_repr(prefix)

    @classmethod
    def construct(cls):
        statement = BlockableStatementComponent.construct()

        if statement is not None:
            cls.parser.expecting_has(r"\n", "EOF")
            return cls(statement)

        return None

    def transpile(self):
        return self.statement.transpile().new(f"{self.indent}%s")

class BlockableStatementComponent(Node):
    @classmethod
    def construct(cls):
        statement = PassStatement.construct() or BreakContinueStatement.construct()
        return statement or ReturnStatement.construct()

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

class ReturnStatement(Node):
    @property
    def nodes(self) -> list:
        return [] if self.expression is None else [self.expression]

    def __init__(self, expression):
        self.expression = expression

    @classmethod
    def construct(cls):
        if not cls.parser.next.has("return"):
            return None

        cls.parser.take()

        if cls.parser.next.has(r"\n", "EOF"):
            return cls(None)

        return cls(Expression.construct())

    def transpile(self):
        statement = self.transpiler.expression("", "return")

        if self.expression is not None:
            statement = statement.new(f"%s {self.expression.transpile()}")

        return statement
