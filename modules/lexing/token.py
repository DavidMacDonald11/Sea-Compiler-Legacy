import re
from functools import cached_property
from string import ascii_letters, ascii_uppercase
from util.misc import escape_whitespace

class Token:
    warnings = None

    @cached_property
    def string(self):
        return escape_whitespace(self.line.string[self.locale[0]:self.locale[1]])

    def __init__(self, line, kind, depth):
        self.line = line
        self.kind = kind
        self.depth = depth
        self.locale = [0, 0]
        self.specifier = None

        self.line += self

    def __repr__(self):
        specifier = "" if self.specifier is None else self.specifier[0]
        return f"{self.kind[0]}{specifier}'{self.string}'"

    def __eq__(self, other):
        return (self.kind, self.string) == other

    def tree_repr(self, _):
        return repr(self)

    def of(self, *kinds):
        return self.kind in kinds

    def has(self, *strings):
        return self.string in strings

    def mark(self):
        self.line.mark(self)

    def validate(self):
        match self.kind:
            case "NumericConstant":
                self._validate_numeric_constant()

    def _validate_numeric_constant(self):
        d_int = re.compile(r"^\d+$")
        d_float = re.compile(r"^\d*.\d*$")

        if d_int.match(self.string):
            self.specifier = "int"
            return

        if "." not in self.string:
            type(self).warnings.error(self, "Incorrect integer constant")
            return

        if d_float.match(self.string):
            self.specifier = "float"
            return

        type(self).warnings.error(self, "Incorrect float constant")

POSTFIX_UNARY_OPERATORS = {"%", "!"}
PREFIX_UNARY_OPERATORS = {"+", "-", "!", "~", "<~", "~>"}
BINARY_OPERATORS = {"^", "*", "/", "+", "-", "<<", ">>", "&", "$", "|"}

OPERATORS = POSTFIX_UNARY_OPERATORS | PREFIX_UNARY_OPERATORS | BINARY_OPERATORS | {"||"}
OPERATOR_SYMBOLS = {c for op in OPERATORS for c in op}

PUNCTUATOR_SYMBOLS = "()"
NUMERIC_START_SYMBOLS = "0123456789."
NUMERIC_SYMBOLS = NUMERIC_START_SYMBOLS
