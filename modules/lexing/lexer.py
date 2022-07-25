from lexing import token
from util.misc import MatchIn
from util.warnings import CompilerError, CompilerWarning
from .source_file import SourceFile

Token = token.Token

class Lexer:
    def __init__(self, options, filepath):
        self.options = options
        self.file = SourceFile(filepath)
        self.at_line_start = True
        self.depth = 0
        self.tokens = []
        self.warnings = []

    def new_token(self, kind, line = None):
        if line is None:
            line = self.file.line

        new_token = Token(line, kind, self.depth)
        self.tokens += [new_token]

        match kind:
            case "CharacterConstant":
                new_token.validate_character_constant(self.warnings)
            case "NumericConstant":
                new_token.validate_numeric_constant(self.warnings)
            case "Identifier":
                new_token.validate_identifier(self.warnings)

        return new_token

    def make_tokens(self):
        self.make_token()

        while self.file.line != "":
            self.make_token()

        for found in self.tokens:
            if not (found.has("\n", "EOF") or found.of("Annotation")):
                break
        else:
            self.warnings += [CompilerWarning("Empty file", None)]

    def make_token(self):
        self.check_spaces()

        match MatchIn(self.file.next):
            case [""]|token.PUNCTUATOR_SYMBOLS:
                self.file.take(1)
                self.new_token("Punctuator")
            case "#":
                self.make_comment()
            case token.NUMERIC_START_SYMBOLS:
                self.make_numeric_constant()
            case token.IDENTIFIER_START_SYMBOLS:
                self.make_identifier()
            case "\"":
                self.make_string_literal()
            case "`'":
                self.make_character_constant()
            case token.OPERATOR_SYMBOLS:
                self.make_operator()
            case _:
                self.file.take(1)
                error = self.new_token("Error")
                error.mark()
                raise CompilerError("Unrecognized symbol", error.line)

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
                indent.warn("Indents must be 4 spaces or 1 tab", self.warnings)
                break
        else:
            self.new_token("Punctuator")

    def make_newline(self):
        if self.file.next != "\n":
            return

        line = self.file.line

        while self.file.next == "\n":
            self.file.take(1)

        self.new_token("Punctuator", line)

    def make_comment(self):
        self.file.take(1)

        if self.file.next == ":":
            self.file.take(1)
            self.new_token("Annotation")
            self.make_raw_block()
        else:
            self.file.take(until = "\n")
            self.new_token("Annotation")

    def make_raw_block(self):
        depth = self.depth + 1
        self.check_spaces()

        if self.file.take(until = "\n") == "pass":
            self.new_token("Keyword")
            self.check_spaces()
            return

        while self.depth >= depth:
            self.file.take(until = "\n")
            self.new_token("Raw")
            self.check_spaces()

    def make_numeric_constant(self):
        if self.file.take(1) == "." and self.file.next not in "0123456789":
            self.new_token("Operator")
            return

        string = self.file.take(these = token.NUMERIC_SYMBOLS)

        if string != "" and string[-1] == "e" and self.file.next in "+-":
            self.file.take(1)
            self.file.take(these = token.NUMERIC_SYMBOLS)

        self.new_token("NumericConstant")

    def make_identifier(self):
        string = self.file.take(these = token.IDENTIFIER_SYMBOLS)

        if string == "\\":
            self.make_line_continuation()
            return

        if string in list(token.STRING_PREFIXES) and self.file.next == "\"":
            self.make_string_literal()
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

        self.new_token("Keyword" if string in token.KEYWORD_LIST else "Identifier")

        if string == "include":
            self.make_include()
        elif string in ("cblock", "ablock") and self.file.next == ":":
            self.file.take(1)
            self.new_token("Punctuator")
            self.make_raw_block()

    def make_line_continuation(self):
        self.file.line.ignore()

        if self.file.next in "\n":
            self.file.take(1)
            self.file.line.ignore()
            return

        self.file.take(1)
        error = self.new_token("Error")
        error.mark()
        raise CompilerError("Unexpected symbol after line continuation character", error.line)

    def make_string_literal(self):
        quotes = self.file.take(3, these = "\"")

        if quotes == "\"\"\"":
            self.make_multiline_string_literal()
            return

        if quotes == "\"\"":
            self.new_token("StringLiteral")
            return

        while True:
            self.file.take(until = "\"\n")

            if self.file.next in "\n":
                string = self.new_token("StringLiteral")
                string.warn("Unterminated string literal", self.warnings)
                return

            if not self.file.line.last_was_slash():
                break

            self.file.take(1)

        self.file.take(1)
        self.new_token("StringLiteral")

    def make_multiline_string_literal(self):
        self.new_token("StringLiteral")

        while True:
            self.file.take(until = "\"\n")

            if self.file.next == "":
                string = self.new_token("StringLiteral")
                string.warn("Unterminated multiline string literal", self.warnings)
                return

            slash = self.file.line.last_was_slash()

            if self.file.next == "\n":
                line = self.file.line

                if not slash:
                    self.file.take(1)

                self.new_token("StringLiteral", line)
                continue

            if slash and self.file.next == "\"":
                self.file.take(1)
                continue

            if self.file.take(3, these = "\"") == "\"\"\"":
                self.new_token("StringLiteral")
                return

    def make_include(self):
        self.check_spaces()

        if self.file.next not in "\"<":
            self.make_file_path(False)
            return

        self.file.take(1)
        lbracket = self.new_token("Punctuator")

        self.make_file_path()

        bracket = "\"" if self.file.take(1) == "\"" else "<"
        rbracket = self.new_token("Punctuator")

        if lbracket.string != bracket:
            rbracket.mark()
            lbracket.warn("Cannot mix \" \" and < > brackets in include statement", self.warnings)

    def make_file_path(self, terminatable = True):
        self.file.take(until = ">\"#\n")
        raw = self.new_token("Raw")

        if terminatable and self.file.next in "\n#":
            raw.warn("Unterminated include statement", self.warnings)

    def make_character_constant(self):
        quote = self.file.take(1)

        if self.file.next != "\\":
            char = self.file.take(1)
            self.file.take(1)
            char_token = self.new_token("CharacterConstant")

            if char == quote:
                char_token.warn("Empty character constant", self.warnings)

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

        end_quote = self.file.take(1)
        char_token = self.new_token("CharacterConstant")

        if end_quote != quote:
            char_token.warn("Unterminated character constant", self.warnings)

        if unknown:
            char_token.warn("Unkown escape sequence", self.warnings)

    def make_operator(self):
        string = ""

        while string + self.file.next in token.OPERATORS:
            string += self.file.take(1)

        self.new_token("Operator")
