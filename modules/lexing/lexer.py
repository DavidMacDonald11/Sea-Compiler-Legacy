from lexing import token
from util.misc import MatchIn
from .source_file import SourceFile

Token = token.Token

class Lexer:
    def __init__(self, warnings, filepath):
        self.warnings = warnings
        self.file = SourceFile(filepath)
        self.at_line_start = True
        self.depth = 0
        self.tokens = []

    def __del__(self):
        self.close()

    def close(self):
        if not self.file.file.closed:
            self.file.file.close()

    def new_token(self, kind, line = None, validate = True):
        if line is None:
            line = self.file.line

        new_token = Token(line, kind, self.depth)
        self.tokens += [new_token]
        if validate: new_token.validate()

        return new_token

    def make_tokens(self):
        self.make_token()

        while self.file.line != "":
            self.make_token()

        for found in self.tokens:
            if not found.of("Punctuator"): break
            if r"\t" in found.string: continue
            if not found.has(r"\n", "EOF"): break
        else:
            self.warnings.error(None, "Empty file")

        tokens = []
        i = 0

        while i < len(self.tokens):
            if self.tokens[i].has(r"\t") and self.tokens[i + 1].has(r"\n"):
                i += 2
            else:
                tokens += [self.tokens[i]]
                i += 1

        self.tokens = tokens

    def make_token(self):
        self.check_spaces()

        match MatchIn(self.file.next):
            case [""]|token.PUNCTUATOR_SYMBOLS:
                self.file.take(1)
                self.new_token("Punctuator")
            case "\\":
                self.make_line_continuation()
            case "#":
                self.make_comment()
            case token.NUMERIC_START_SYMBOLS:
                self.make_numeric_constant()
            case "'":
                self.make_character_constant()
            case '"':
                self.make_string_constant()
            case token.IDENTIFIER_START_SYMBOLS:
                self.make_identifier()
            case token.OPERATOR_SYMBOLS:
                self.make_operator()
            case _:
                self.file.take(1)
                raise self.warnings.fail(self.new_token("Error"), "Unrecognized symbol")

    def check_spaces(self):
        if not self.file.next.isspace():
            self.at_line_start = False
        else:
            self.make_spaces()

    def make_spaces(self):
        if self.at_line_start:
            self.make_indents()
            self.make_newline()
        else:
            self.file.take(these = " \t")
            self.file.line.ignore()

            if self.file.next == "\n":
                self.at_line_start = True

        self.check_spaces()

    def make_indents(self):
        self.depth = 0

        if self.file.next == "\n":
            return

        while self.file.next in " \t":
            string = self.file.take(4, these = " ") if self.file.next == " " else self.file.take(1)
            self.depth += 1

            if string not in [" " * 4, "\t"]:
                indent = self.new_token("Punctuator")
                self.warnings.warn(indent, "Indents must be 4 spaces or 1 tab")
                break
        else:
            self.new_token("Punctuator")

    def make_newline(self):
        if self.file.next != "\n":
            return

        line = self.file.line

        while self.file.next == "\n":
            self.file.take(1)

            if self.file.next == "#":
                self.make_comment()

        self.new_token("Punctuator", line)

    def make_line_continuation(self):
        self.file.take(1)
        self.file.take(these = " \t")
        self.file.line.ignore()

        if self.file.take(1) in "\n":
            self.file.line.ignore()
            return

        symbol = self.new_token("Error")
        self.warnings.error(symbol, "Unexpected symbol after line continuation character")

    def make_comment(self):
        self.file.take(until = "\n")
        self.file.line.ignore()

    def make_numeric_constant(self):
        if self.file.take(1) == "." and self.file.next not in "0123456789":
            self.new_token("Operator")
            return

        self.file.take(these = token.NUMERIC_SYMBOLS)
        self.new_token("NumericConstant")

    def make_character_constant(self):
        self.file.take(1)

        if self.file.next != "\\":
            char = self.file.take(1)
            self.file.take(1)
            self.new_token("CharacterConstant")
            return

        self.file.take(1)
        escape = self.file.take(1)
        unknown = False

        match MatchIn(escape):
            case "01234567":
                self.file.take(these = "01234567")
            case "abfnrtv'`\"\\?":
                pass
            case "xuU":
                self.file.take(these = "0123456789ABCDEF")
            case _:
                unknown = True

        self.file.take(1)
        char = self.new_token("CharacterConstant", validate = not unknown)

        if unknown:
            self.warnings.error(char, "Unknown escape sequence")

    def make_identifier(self):
        string = self.file.take(these = token.IDENTIFIER_SYMBOLS)

        if string in list(token.STRING_PREFIXES) and self.file.next == '"':
            self.make_string_constant()
            return

        if string == "__operator":
            self.file.take(these = token.OPERATOR_SYMBOLS)
            self.file.take(these = "_")
        elif string[:2] == "__":
            operator = self.file.take(these = token.OPERATOR_SYMBOLS)
            self.file.take(these = token.IDENTIFIER_SYMBOLS)

            if operator == "||":
                self.file.take(2, these = "|")
                self.file.take(these = "_")

        self.new_token("Keyword" if string in token.KEYWORDS else "Identifier")

    def make_operator(self):
        string = ""

        while string + self.file.next in token.OPERATORS:
            string += self.file.take(1)

        self.new_token("Operator")

    def make_string_constant(self):
        quotes = self.file.take(3, these = '"')

        if quotes == '"""':
            self.make_multiline_string_constant()
            return

        if quotes == '""':
            self.new_token("StringConstant")
            return

        while True:
            self.file.take(until = '"\n')

            if self.file.next in "\n":
                string = self.new_token("StringConstant")
                self.warnings.error(string, "Unterminated string")
                return

            if not self.file.line.last_was_slash():
                break

            self.file.take(1)

        self.file.take(1)
        self.new_token("StringConstant")

    def make_multiline_string_constant(self):
        while True:
            self.file.take(until = '"\n')

            if self.file.next == "":
                string = self.new_token("StringConstant")
                self.warnings.error(string, "Unterminated multiline string")
                return

            slash = self.file.line.last_was_slash()

            if self.file.next == "\n":
                line = self.file.line

                if not slash:
                    self.file.take()

                self.new_token("StringConstant", line)
                continue

            if slash and self.file.next == '"':
                self.file.take(1)
                continue

            if self.file.take(3, these = '"') == '"""':
                self.new_token("StringConstant")
                return
