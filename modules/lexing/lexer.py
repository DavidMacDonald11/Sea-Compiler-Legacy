from string import ascii_letters, ascii_uppercase
from util.warnings import CompilerError
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
        if len(self.symbols) == 0:
            raise CompilerError("Expecting symbol", self.take_string(take = False))

        return self.symbols[0]

    @property
    def last(self):
        return self.string.symbols[-1]

    def __init__(self, filepath):
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
        self.make_spaces()

        if self.symbols == "":
            self += Punctuator(self.take_string(take = False))
            return

        if self.symbol in Punctuator.SYMBOLS:
            self += Punctuator(self.take_string(1))
            return

        if self.symbol in "0123456789.":
            return self.make_numeric_constant()

        if self.symbol in f"{ascii_letters}_\\":
            return self.make_identifier()

        if self.symbol in "`'":
            return self.make_character_constant()

        if self.symbol in "\"":
            return self.make_string_literal()

        if self.symbol in Operator.SYMBOLS:
            return self.make_operator()

        raise CompilerError("Unrecognized symbol", self.take_string(1))

    def make_spaces(self):
        if not self.symbols.isspace():
            self.at_line_start = False
            return

        if not self.at_line_start:
            self.take_string(until = "\n")

            if self.symbol != "\n":
                return

            self.at_line_start = True
            return self.make_spaces()

        if self.symbol in "\t\n":
            self += Punctuator(self.take_string(1))
            return self.make_spaces()

        if self.symbols[:4] != " " * 4:
            string = self.take_string(until = "\t\n")
            raise CompilerError("Indents must be 4 spaces or 1 tab", string)

        self += Punctuator(self.take_string(4))
        return self.make_spaces()

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
            else:
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
            return self.make_string_literal()

        self += StringLiteral(self.take_string(1))

    def make_operator(self):
        symbols = ""

        while symbols + self.symbol in Operator.LIST:
            symbols += self.take(1)

        self += Operator(self.take_string(take = False))
