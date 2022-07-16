import re
from functools import cached_property
from string import ascii_letters, ascii_uppercase
from util.warnings import CompilerWarning

class Token:
    @cached_property
    def string(self):
        return self.line.string[self.locale[0]:self.locale[1]]

    def __init__(self, kind, line):
        self.kind = kind
        self.line = line
        self.locale = [0, 0]

        self.line += self

    def __repr__(self):
        string = self.string.replace("\n", r"\n").replace("    ", r"\t")
        return f"{self.kind[0]}'{string}'"

    def of(self, *kinds):
        return any(kind in self.kind for kind in kinds)

    def has(self, *strings):
        return self.string in strings

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
            return None

        if "." not in self.string and "e" not in self.string:
            return CompilerWarning("Incorrect integer constant", self)

        is_float = d_float.match(self.string) or dn_float.match(self.string)
        is_float = is_float or nd_float.match(self.string)

        if is_float or n_float.match(self.string):
            return None

        return CompilerWarning("Incorrect float constant", self)

    def validate_identifier(self):
        pattern = re.compile(r"^(\w*\\((u[0-9A-F]{4})|(U[0-9A-F]{8})))*\w*$")

        if pattern.match(self.string):
            return None

        return CompilerWarning("Incorrect universal character name", self)

KEYWORD_LIST = (
        "alias", "align", "aligned", "alloc", "and", "as", "asm",
        "assert", "atomic", "auto", "block", "bool", "break", "bytes",
        "c", "char", "complex", "const", "continue", "dealloc",
        "decorate", "define", "defined", "deviant", "do", "double",
        "else", "enum", "external", "False", "float", "for", "if",
        "in", "is", "imaginary", "include", "Infinity", "inline",
        "int", "local", "long", "manage", "match", "mod", "NaN", "not",
        "Null", "of", "or", "pass", "Pi", "real", "realloc", "redefine",
        "register", "restrict", "return", "short", "size", "static",
        "str", "struct", "template", "thread", "to", "True", "type",
        "undefine", "union", "void", "volatile", "while", "with", "yield"
    )

OPERATOR_LIST = (
        ".", "->", "++", "--", "%", "!",
        "^", "@", "-", "~", "~<", "~>", "*",
        "**", "/", "+", "<<", ">>", "&", "|", "$",
        "<", ">", "<=", ">=", "==", "!=", "<=>",
        "=", "**=", "*=", "/=", "%=", "+=", "-=",
        "<<=", ">>=", "&=", "|=", "$="
    )

OPERATOR_SYMBOLS = {c for op in OPERATOR_LIST for c in op }
STRING_PREFIXES = "bBfFrR"
PUNCTUATOR_SYMBOLS = "[](){},:"
NUMERIC_START_SYMBOLS = "0123456789."
NUMERIC_SYMBOLS = f"{NUMERIC_START_SYMBOLS}{ascii_uppercase}.be"
IDENTIFIER_START_SYMBOLS = f"{ascii_letters}_\\"
IDENTIFIER_SYMBOLS = f"{IDENTIFIER_START_SYMBOLS}0123456789"
