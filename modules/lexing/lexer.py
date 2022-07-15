from functools import cached_property
from string import ascii_letters, ascii_uppercase
from util.misc import MatchIn
from util.warnings import CompilerError
from .tokens.annotation import Annotation
from .tokens.character_constant import CharacterConstant
from .tokens.identifier import Identifier
from .tokens.keyword import Keyword
from .tokens.numeric_constant import NumericConstant
from .tokens.operator import Operator
from .tokens.punctuator import Punctuator
from .tokens.string_literal import StringLiteral
from .tokens.token_string import TokenString

class Lexer:
    @property
    def symbol(self):
        return "" if len(self.symbols) == 0 else self.symbols[0]

    @property
    def last(self):
        return self.string.symbols[-1]

    @cached_property
    def keep_comments(self):
        return "t" in self.options

    def __init__(self, options, filepath):
        self.options = options
        self.file = open(filepath, "r", encoding = "UTF-8")
        self.string = TokenString(filepath, "", [1, 1])
        self.at_line_start = True
        self.symbols = ""
        self.tokens = []

        self.next()

    def __iadd__(self, token):
        self.tokens += [token]
        return self

    def __del__(self):
        self.file.close()

    def next(self):
        if self.symbols != "":
            return self.symbols

        symbol = self.file.read(1)

        while symbol != "":
            is_different = (self.symbols.isspace() != symbol.isspace())

            if self.symbols != "" and is_different:
                self.file.seek(self.file.tell() - 1)
                break

            self.symbols += symbol
            symbol = self.file.read(1)

        return self.symbols

    def take(self, num = 0, inside = "", until = "", refresh = False):
        taken = ""

        if inside == "":
            condition = lambda x: x not in until
        else:
            condition = lambda x: x not in until and x in inside

        while len(self.symbols) > 0 and condition(self.symbol):
            self.string += self.symbol
            taken += self.symbol
            self.symbols = self.symbols[1:]

            if refresh:
                self.next()

            if num != 0 and len(taken) == num:
                break

        if len(self.symbols) == 0:
            self.next()

        return taken

    def take_string(self, num = 0, inside = "", until = "", take = True):
        if take:
            self.take(num, inside, until)

        string = self.string
        self.string = string.next()
        return string

    def make_tokens(self):
        while self.symbols != "":
            self.make_token()

    def make_token(self):
        self.check_spaces()

        match MatchIn(self.symbol):
            case [""]|Punctuator.SYMBOLS:
                self += Punctuator(self.take_string(1))
            case "#":
                self.make_comment()
            case "0123456789.":
                self.make_numeric_constant()
            case Identifier.START:
                self.make_identifier()
            case "`'":
                self.make_character_constant()
            case "\"":
                self.make_string_literal()
            case Operator.SYMBOLS:
                self.make_operator()
            case _:
                raise CompilerError("Unrecognized symbol", self.take_string(1))

    def check_spaces(self):
        if not self.symbols.isspace():
            self.at_line_start = False
        else:
            self.make_spaces()

    def make_spaces(self):
        if not self.at_line_start:
            self.take_string(until = "\n")

            if self.symbol == "\n":
                self.at_line_start = True
                self.check_spaces()

            return

        if self.symbol in "\t\n":
            self += Punctuator(self.take_string(1))
            self.check_spaces()
            return

        if self.symbols[:4] != " " * 4:
            string = self.take_string(until = "\t\n")
            raise CompilerError("Indents must be 4 spaces or 1 tab", string)

        self += Punctuator(self.take_string(4))
        self.check_spaces()

    def make_comment(self):
        self.take(until = "\n", refresh = True)
        string = self.take_string(take = False)

        if self.keep_comments:
            self += Annotation(string)

    def make_numeric_constant(self):
        self.take(1)

        if self.last == "." and self.symbol not in "0123456789":
            self += Operator(self.take_string(take = False))
            return

        self.take(inside = f"{ascii_uppercase}0123456789.be")

        if self.last == "e" and self.symbol in "+-":
            self.take(1)
            self.take(inside = f"{ascii_uppercase}0123456789b")

        self += NumericConstant(self.take_string(take = False))

    def make_identifier(self):
        symbols = self.take(inside = f"{ascii_letters}_\\0123456789")

        string_prefix = len(symbols) == 1 and symbols in StringLiteral.PREFIXES

        if string_prefix and self.symbol == "\"":
            self.make_string_literal()
            return

        string = self.take_string(take = False)
        self += (Keyword if symbols in Keyword.LIST else Identifier)(string)

    def make_character_constant(self):
        def finish_character(self, quote):
            if quote != self.symbol:
                string = self.take_string(1)
                raise CompilerError("Unterminated character constant", string)

            self += CharacterConstant(self.take_string(1))

        quote = self.take(1)

        if self.symbol == quote:
            string = self.take_string(1)
            raise CompilerError("Empty character constant", string)

        if self.symbol != "\\":
            self.take(1)
            return finish_character(self, quote)

        self.take(1)
        escape = self.take(1)

        if escape in "01234567":
            self.take(inside = "01234567")
            return finish_character(self, quote)

        if escape in "abfnrtv'`\"\\?":
            return finish_character(self, quote)

        if escape in "xuU":
            self.take(inside = "0123456789ABCDEF")
            return finish_character(self, quote)

        string = self.take_string(take = False)
        raise CompilerError("Incorrect character constant", string)

    def make_string_literal(self):
        self.take(1)
        self.take(until = "\"\n", refresh = True)

        if self.symbol == "\n":
            string = self.take_string(take = False)
            raise CompilerError("Unterminated string literal", string)

        if self.string.symbols.replace(r"\\", "")[-1] == "\\":
            self.make_string_literal()
            return

        self += StringLiteral(self.take_string(1))

    def make_operator(self):
        symbols = ""

        while symbols + self.symbol in Operator.LIST:
            symbols += self.take(1)

        self += Operator(self.take_string(take = False))
