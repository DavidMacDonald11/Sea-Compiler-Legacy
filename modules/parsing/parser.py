from util.misc import repr_expand
from .expressions.unary_expression import UnaryExpression
from .expressions.expression import Expression
from .statements.statement import Statement
from .statements.file_statement import FileStatement

class Parser:
    @property
    def next(self):
        self.i = min(self.i, len(self.tokens) - 1)
        return self.tokens[self.i]

    def __init__(self, warnings, tokens):
        self.warnings = warnings
        self.tokens = tokens
        self.i = 0
        self.indents = 0
        self.tree = None

    def make_tree(self):
        self.tree = FileStatement.construct()
        self.tree.make_tree(self)

    def take(self):  # sourcery skip: inline-immediately-returned-variable
        token = self.next
        self.i += 1
        return token

    def ignore_spaces(self):
        while self.next.has(r"\n", r"\t"):
            self.take()

    def expecting_of(self, *kinds):
        if self.next.of(*kinds):
            return self.take()

        raise self.warnings.fail(self.take(), f"Expecting {repr_expand(kinds)}")

    def expecting_has(self, *strings):
        if self.next.has(*strings):
            return self.take()

        raise self.warnings.fail(self.take(), f"Expecting {repr_expand(strings)}")

    def verify_indent(self):
        tab_next = self.next.has(r"\t")

        if not tab_next and self.indents == 0:
            return None

        indent = self.take()

        if tab_next and indent.depth == self.indents:
            return indent

        self.warnings.warn(indent, f"Expecting {self.indents} indents")

    @property
    def expression(self):
        return Expression

    @property
    def statement(self):
        return Statement

    @property
    def unary_expression(self):
        return UnaryExpression
