import re
from functools import cached_property
from string import ascii_letters, ascii_uppercase
from util.misc import escape_whitespace, MatchRe

class FakeToken:
    warnings = None

    @cached_property
    def string(self):
        return self._string

    @classmethod
    def copy(cls, token, string = None):
        return cls(token.line, token.kind, token.depth, string or token.string, token)

    def __init__(self, line, kind, depth, string, token = None):
        self.token = token or self
        self.line = line
        self.kind = kind
        self.depth = depth
        self.specifier = None
        self._string = string

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
        self.line.mark(self.token)

    def validate(self):
        match self.kind:
            case "NumericConstant":
                self._validate_numeric_constant()
            case "CharacterConstant":
                self._validate_character_constant()
            case "Identifier":
                self._validate_identifier()

    def _validate_numeric_constant(self):
        d_int = re.compile(r"^\d+$")
        n_int = re.compile(r"^\d+b[A-Z0-9]+$")

        if d_int.match(self.string) or n_int.match(self.string):
            self.specifier = "i"
            return

        if "." not in self.string and "e" not in self.string:
            type(self).warnings.error(self, "Incorrect integer constant")
            return

        patterns = [re.compile(r"^\d*.?\d*(e[+-]?\d+)?$")]
        patterns += [re.compile(r"^\d*.?\d*(e[+-]?\d+b[A-Z0-9]+)?$")]
        patterns += [re.compile(r"^\d+b[A-Z0-9]*.?[A-Z0-9]*(e[+-]?\d+)?$")]
        patterns += [re.compile(r"^\d+b[A-Z0-9]*.?[A-Z0-9]*(e[+-]?\d+b[A-Z0-9]+)?$")]

        for pattern in patterns:
            if pattern.match(self.string):
                self.specifier = "f"
                return

        type(self).warnings.error(self, "Incorrect float constant")

    def _validate_character_constant(self):
        patterns = [re.compile(r"^'[^\\]'$")]
        patterns += [re.compile(r"^'\\[abfnrtv'\"\\?]'$")]
        patterns += [re.compile(r"^'\\[0-7]{1, 3}'$")]
        patterns += [re.compile(r"^'\\x[0-9A-F]+'$")]
        patterns += [re.compile(r"^'\\u[0-9A-F]{4}'$")]
        patterns += [re.compile(r"^'\\U[0-9A-F]{8}'$")]

        for pattern in patterns:
            if pattern.match(self.string):
                return

        match MatchRe(self.string):
            case r"^''$":
                message = "Empty character constant"
            case r"^'[^']*$":
                message = "Unterminated character constant"
            case _:
                message = "Incorrect character constant"

        type(self).warnings.error(self, message)

    def _validate_identifier(self):
        pattern = re.compile(r"^\w+$")

        if pattern.match(self.string):
            return

        if self.string in OPERATOR_FUNCS:
            if self.string in DISALLOWED_OPERATOR_FUNCS:
                op = DISALLOWED_OPERATOR_FUNCS[self.string]
                type(self).warnings.error(self, f"Cannot overload {op} operator")

            return

        type(self).warnings.error(self, "Incorrect operator function")

class Token(FakeToken):
    warnings = None

    @cached_property
    def string(self):
        return escape_whitespace(self.line.string[self.locale[0]:self.locale[1]])

    def __init__(self, line, kind, depth):
        self.locale = [0, 0]
        super().__init__(line, kind, depth, "")
        self.line += self

POSTFIX_UNARY_OPERATORS = {"%", "!", "?"}
PREFIX_UNARY_OPERATORS = {"+", "-", "!", "~", "<~", "~>", "&", "$"}
BINARY_OPERATORS = {"^", "*", "/", "+", "-", "<<", ">>", "&", "$", "|", "<=>"}
COMPARATIVE_OPERATORS = {"<", ">", "<=", ">=", "==", "!="}
ASSIGNMENT_OPERATORS = {"=", "^=", "*=", "/=", "%=", "+=", "-=", "<<=", ">>=", "&=", "$=", "|="}

POSTFIX_OPERATORS = POSTFIX_UNARY_OPERATORS | BINARY_OPERATORS | COMPARATIVE_OPERATORS
POSTFIX_OPERATORS |= ASSIGNMENT_OPERATORS

OPERATORS = PREFIX_UNARY_OPERATORS | POSTFIX_OPERATORS | {"||"}
OPERATOR_SYMBOLS = {c for op in OPERATORS for c in op}

PRIMARY_KEYWORDS = {"True", "False"}
INT_TYPE_KEYWORDS = {"int"} | {f"int{2 ** x}" for x in range(3, 7)}
NAT_TYPE_KEYWORDS = {"bool", "char"} | {"nat"} | {f"nat{2 ** x}" for x in range(3, 7)}
FLOAT_TYPE_KEYWORDS = {"real", "imag", "cplex"}
FLOAT_TYPE_KEYWORDS |= {f"{t}{2 ** x}" for x in range(5, 7) for t in FLOAT_TYPE_KEYWORDS}
TYPE_KEYWORDS = INT_TYPE_KEYWORDS | NAT_TYPE_KEYWORDS | FLOAT_TYPE_KEYWORDS
TYPE_MODIFIER_KEYWORDS = {"var", "invar"}
KEYWORDS = PRIMARY_KEYWORDS | TYPE_KEYWORDS | TYPE_MODIFIER_KEYWORDS | {
    "mod", "not", "and", "or", "as", "if", "else", "pass"
}

PUNCTUATOR_SYMBOLS = "(),[]:"
NUMERIC_START_SYMBOLS = "0123456789."
NUMERIC_SYMBOLS = NUMERIC_START_SYMBOLS + ascii_uppercase + "be+-"
IDENTIFIER_START_SYMBOLS = f"{ascii_letters}_"
IDENTIFIER_SYMBOLS = f"{IDENTIFIER_START_SYMBOLS}0123456789"

OPERATOR_FUNCS = {"__||operator||__"} | {f"__{x}operator__" for x in PREFIX_UNARY_OPERATORS}
OPERATOR_FUNCS |= {f"__operator{x}__" for x in POSTFIX_OPERATORS}
DISALLOWED_OPERATOR_FUNCS = {"__&operator__": "prefix &"}
