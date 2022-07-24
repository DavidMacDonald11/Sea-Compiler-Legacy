import re
from functools import cached_property
from string import ascii_letters, ascii_uppercase
from util.misc import escape_whitespace
from util.warnings import CompilerWarning

class Token:
    @cached_property
    def string(self):
        return self.line.string[self.locale[0]:self.locale[1]]

    def __init__(self, kind, line):
        self.kind = kind
        self.line = line
        self.locale = [0, 0]
        self.specifier = None

        self.line += self

    def __repr__(self):
        return f"{self.kind[0]}'{escape_whitespace(self.string)}'"

    def __eq__(self, other):
        return (self.kind, self.string) == other

    def tree_repr(self, _):
        return f"{self}\n"

    def of(self, *kinds):
        return self.kind in kinds

    def has(self, *strings):
        return self.string in strings

    def may_be_type(self):
        return not self.has("not") if self.of("Keyword") else self.has("+")

    def mark(self):
        self.line.mark(self)

    def raw(self):
        line = self.line.number
        col1, col2 = self.locale
        file = self.line.filename

        string = f"{file}: Ln{line}, Col {col1 + 1} to Col {col2 + 1}\n"
        string += f"{line:4d}|{self.line.string}"
        string += "    |" + " " * col1 + "^" * (col2 - col1)

        return string

    def validate_character_constant(self):
        patterns = []
        patterns += [re.compile(r"^('|`)[^\\]\1$")]
        patterns += [re.compile(r"^('|`)\\[abfnrtv'`\"\\?]\1$")]
        patterns += [re.compile(r"^('|`)\\[0-7]{1, 3}\1$")]
        patterns += [re.compile(r"^('|`)\\x[0-9A-F]+\1$")]
        patterns += [re.compile(r"^('|`)\\u[0-9A-F]{4}\1$")]
        patterns += [re.compile(r"^('|`)\\U[0-9A-F]{8}\1$")]

        for pattern in patterns:
            if pattern.match(self.string):
                return None

        return CompilerWarning("Incorrect character constant", self)

    def validate_numeric_constant(self):
        d_int = re.compile(r"^\d+$")
        n_int = re.compile(r"^\d+b[A-Z0-9]+$")
        d_float = re.compile(r"^\d*.?\d*(e[+-]?\d+)?$")
        dn_float =  re.compile(r"^\d*.?\d*(e[+-]?\d+b[A-Z0-9]+)?$")
        nd_float = re.compile(r"^\d+b[A-Z0-9]*.?[A-Z0-9]*(e[+-]?\d+)?$")
        n_float = re.compile(r"^\d+b[A-Z0-9]*.?[A-Z0-9]*(e[+-]?\d+b[A-Z0-9]+)?$")

        if d_int.match(self.string) or n_int.match(self.string):
            self.specifier = "int"
            return None

        if "." not in self.string and "e" not in self.string:
            return CompilerWarning("Incorrect integer constant", self)

        is_float = d_float.match(self.string) or dn_float.match(self.string)
        is_float = is_float or nd_float.match(self.string)

        if is_float or n_float.match(self.string):
            self.specifier = "float"
            return None

        return CompilerWarning("Incorrect float constant", self)

    def validate_identifier(self):
        op_pattern = re.compile(r"^_+\W*operator\W*_*$")
        pattern = re.compile(r"^(\w*\\((u[0-9A-F]{4})|(U[0-9A-F]{8})))*\w*$")

        if pattern.match(self.string):
            return None

        if op_pattern.match(self.string):
            if self.string in OPERATOR_IDENTIFIERS:
                return None

            return CompilerWarning("Incorrect operator identifier", self)

        return CompilerWarning("Incorrect universal character name", self)

PRIMARY_KEYWORD_LIST = ("False", "Null", "True")

KEYWORD_LIST = PRIMARY_KEYWORD_LIST + (
        "alias", "align", "aligned", "alloc", "and", "as", "asm",
        "assert", "atomic", "auto", "block", "bool", "break",
        "clang", "char", "complex", "const", "continue", "dealloc",
        "decorate", "define", "defined", "deviant", "do", "double",
        "else", "enum", "external", "float", "for", "func", "if",
        "in", "is", "imaginary", "include", "inline",
        "int", "local", "long", "manage", "match", "mod", "not",
        "Null", "of", "or", "pass", "real", "realloc", "redefine",
        "register", "restrict", "return", "short", "size", "static",
        "str", "struct", "template", "thread", "to", "type",
        "undefine", "union", "void", "volatile", "while", "with", "yield"
    )

UNARY_OPERATOR_LIST = ("^", "@", "-", "!", "~", "~<", "~>", "*")

COMPARATIVE_OPERATOR_LIST = ("<", ">", "<=", ">=", "==", "!=", "<=>")

ASSIGNMENT_OPERATOR_LIST = (
    "=", "**=", "*=", "/=", "%=", "+=", "-=",
    "<<=", ">>=", "&=", "|=", "$="
    )

REMAINING_OPERATOR_LIST = COMPARATIVE_OPERATOR_LIST + ASSIGNMENT_OPERATOR_LIST + (
    ".", "->", "++", "--", "%",
    "**", "/", "+", "<<", ">>", "&", "|", "$",
    "||"
    )

OPERATOR_LIST = UNARY_OPERATOR_LIST + REMAINING_OPERATOR_LIST

OPERATOR_SYMBOLS = {c for op in OPERATOR_LIST for c in op }
STRING_PREFIXES = "bBfFrR"
PUNCTUATOR_SYMBOLS = "[](){},:"
NUMERIC_START_SYMBOLS = "0123456789."
NUMERIC_SYMBOLS = f"{NUMERIC_START_SYMBOLS}{ascii_uppercase}.be"
IDENTIFIER_START_SYMBOLS = f"{ascii_letters}_\\"
IDENTIFIER_SYMBOLS = f"{IDENTIFIER_START_SYMBOLS}0123456789"

OPERATOR_IDENTIFIERS = {f"__{x}operator__" for x in UNARY_OPERATOR_LIST} | {
    "__||operator||__",
    "__opeartor!__",
    "__operator-__",
    "__operator*__",
    "__++operator__",
    "__--operator__",
} | {f"__operator{x}" for x in REMAINING_OPERATOR_LIST}
