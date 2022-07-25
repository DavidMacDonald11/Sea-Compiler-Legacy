import re
from functools import cached_property
from string import ascii_letters, ascii_uppercase
from util.misc import escape_whitespace
from util.warnings import CompilerWarning

class Token:
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
        return f"{self.kind[0]}'{self.string}'"

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

    def warn(self, message, warnings):
        self.mark()
        warnings += [CompilerWarning(message, self.line)]

    def validate_character_constant(self, warnings):
        patterns = []
        patterns += [re.compile(r"^('|`)[^\\]\1$")]
        patterns += [re.compile(r"^('|`)\\[abfnrtv'`\"\\?]\1$")]
        patterns += [re.compile(r"^('|`)\\[0-7]{1, 3}\1$")]
        patterns += [re.compile(r"^('|`)\\x[0-9A-F]+\1$")]
        patterns += [re.compile(r"^('|`)\\u[0-9A-F]{4}\1$")]
        patterns += [re.compile(r"^('|`)\\U[0-9A-F]{8}\1$")]

        for pattern in patterns:
            if pattern.match(self.string):
                return

        self.warn("Incorrect character constant", warnings)

    def validate_numeric_constant(self, warnings):
        d_int = re.compile(r"^\d+$")
        n_int = re.compile(r"^\d+b[A-Z0-9]+$")
        d_float = re.compile(r"^\d*.?\d*(e[+-]?\d+)?$")
        dn_float =  re.compile(r"^\d*.?\d*(e[+-]?\d+b[A-Z0-9]+)?$")
        nd_float = re.compile(r"^\d+b[A-Z0-9]*.?[A-Z0-9]*(e[+-]?\d+)?$")
        n_float = re.compile(r"^\d+b[A-Z0-9]*.?[A-Z0-9]*(e[+-]?\d+b[A-Z0-9]+)?$")

        if d_int.match(self.string) or n_int.match(self.string):
            self.specifier = "int"
            return

        if "." not in self.string and "e" not in self.string:
            self.warn("Incorrect integer constant", warnings)
            return

        is_float = d_float.match(self.string) or dn_float.match(self.string)
        is_float = is_float or nd_float.match(self.string)

        if is_float or n_float.match(self.string):
            self.specifier = "float"
            return

        self.warn("Incorrect float constant", warnings)

    def validate_identifier(self, warnings):
        op_pattern = re.compile(r"^_+\W*operator\W*_*$")
        pattern = re.compile(r"^(\w*\\((u[0-9A-F]{4})|(U[0-9A-F]{8})))*\w*$")

        if pattern.match(self.string):
            return

        if op_pattern.match(self.string):
            if self.string in OPERATOR_IDENTIFIERS:
                return

            self.warn("Incorrect operator identifier", warnings)
            return

        self.warn("Incorrect universal character name", warnings)

PRIMARY_KEYWORD_LIST = ("False", "Null", "True")

KEYWORD_LIST = PRIMARY_KEYWORD_LIST + (
    "ablock", "alias", "align", "aligned", "alloc", "and", "as",
    "assert", "atomic", "auto", "block", "bool", "break",
    "cblock", "char", "complex", "const", "continue", "dealloc",
    "decorate", "define", "defined", "deviant", "do", "double",
    "else", "enum", "external", "float", "for", "func", "if",
    "in", "is", "imaginary", "include", "inline",
    "int", "local", "long", "manage", "match", "mod", "not",
    "Null", "of", "or", "pass", "real", "realloc", "redefine",
    "register", "restrict", "return", "short", "size", "static",
    "str", "struct", "template", "thread", "to", "type",
    "undefine", "union", "void", "volatile", "while", "with", "yield"
)

POSTFIX_OPERATORS = {".", "->", "++", "--", "%", "!"}
PREFIX_OPERATORS = {"^", "@", "+", "-", "!", "~", "~<", "~>", "*", "++", "--"}
BINARY_OPERATORS = {"**", "*", "/", "+", "-", "<<", ">>", "&", "$", "|"}
COMPARATIVE_OPERATORS = {"<", ">", "<=", ">=", "==", "!=", "<=>"}
ASSIGNMENT_OPERATORS = {"=", "**=", "*=", "/=", "%=", "+=", "-=", "<<=", ">>=", "&=", "|=", "$="}

OPERATORS = POSTFIX_OPERATORS | PREFIX_OPERATORS | BINARY_OPERATORS
OPERATORS |= COMPARATIVE_OPERATORS | ASSIGNMENT_OPERATORS | {"||"}
OPERATOR_SYMBOLS = {c for op in OPERATORS for c in op }

STRING_PREFIXES = "bBfFrR"
PUNCTUATOR_SYMBOLS = "[](){},:"
NUMERIC_START_SYMBOLS = "0123456789."
NUMERIC_SYMBOLS = f"{NUMERIC_START_SYMBOLS}{ascii_uppercase}.be"
IDENTIFIER_START_SYMBOLS = f"{ascii_letters}_\\"
IDENTIFIER_SYMBOLS = f"{IDENTIFIER_START_SYMBOLS}0123456789"

OPERATOR_IDENTIFIERS_POST_OPS = POSTFIX_OPERATORS | BINARY_OPERATORS | COMPARATIVE_OPERATORS
OPERATOR_IDENTIFIERS_POST_OPS |= ASSIGNMENT_OPERATORS
OPERATOR_IDENTIFIERS = {"__||operator||__"} | {f"__{x}operator__" for x in PREFIX_OPERATORS}
OPERATOR_IDENTIFIERS |= {f"__operator{x}__" for x in OPERATOR_IDENTIFIERS_POST_OPS}
