from lexing import token
from util.misc import MatchIn
from util.warnings import CompilerError, CompilerWarning
from .smart_file import SmartFile

Token = token.Token

class Lexer:
    @property
    def string(self):
        return self.file.line.string

    def __init__(self, options, filepath):
        self.file = SmartFile(filepath)
        self.at_line_start = True
        self.keep_comments = "t" in options
        self.tokens = []
        self.warnings = []
        self.depth = 0

    def new_token(self, kind, line = None):
        if line is None:
            line = self.file.line

        new_token = Token(kind, line)
        self.tokens += [new_token]
        warning = None

        match kind:
            case "CharacterConstant":
                warning = new_token.validate_character_constant()
            case "NumericConstant":
                warning = new_token.validate_numeric_constant()
            case "Identifier":
                warning = new_token.validate_identifier()

        if warning is not None:
            self.warnings += [warning]

        return new_token

    def warn(self, message):
        self.tokens[-1].mark()
        self.warnings += [CompilerWarning(message, self.tokens[-1].line)]

    def make_tokens(self):
        self.make_token()

        while self.string != "":
            self.make_token()

        if len(self.tokens) == 0 or self.tokens[-1].string != "":
            self.file.take(1)
            self.new_token("Punctuator")

        for found in self.tokens:
            if not (found.has("\n", "") or found.of("Annotation")):
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
                self.new_token("ERROR")
                raise CompilerError("Unrecognized symbol", self.tokens[-1].line)

    def check_spaces(self):
        if not self.file.next.isspace():
            self.at_line_start = False
        else:
            self.make_spaces()

    def make_spaces(self):
        if self.at_line_start:
            self.make_indents()
            self.check_spaces()
            return

        self.file.take(these = " \t")
        self.file.line.ignore()

        if self.file.next == "\n":
            self.depth = 0
            self.at_line_start = True

        self.check_spaces()

    def make_indents(self):
        if self.file.next in "\t\n":
            line = self.file.line
            taken = self.file.take(1)
            self.depth += 1 if taken == "\t" else -self.depth
            self.new_token("Punctuator", line)
            return

        string = self.file.take(4, these = " ")
        self.depth += 1
        self.new_token("Punctuator")

        if string != " " * 4:
            self.warn("Indents must be 4 spaces or 1 tab")

    def make_comment(self):
        self.file.take(until = "\n")

        if self.keep_comments:
            self.new_token("Annotation")
        else:
            self.file.line.ignore()

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
        is_prefix = len(string) == 1 and string[0] in token.STRING_PREFIXES

        if is_prefix and self.file.next == "\"":
            self.make_string_literal()
            return

        if string == "__operator":
            self.file.take(these = token.OPERATOR_SYMBOLS)
            self.file.take(these = "_")
        elif len(string) > 1 and string[:2] == "__":
            operator = self.file.take(these = token.OPERATOR_SYMBOLS)
            self.file.take(these = token.IDENTIFIER_SYMBOLS)

            if operator == "||":
                self.file.take(2, these = "|")

            self.file.take(these = "_")

        kind = "Keyword" if string in token.KEYWORD_LIST else "Identifier"
        self.new_token(kind)

        if string in ("include",):
            self.make_include()

        if string in ("clang", "asm"):
            self.make_raw_block()

    def make_string_literal(self):
        self.file.take(1)
        self.file.take(until = "\"\n")

        if self.file.next == "\n":
            self.new_token("StringLiteral")
            self.warn("Unterminated string literal")
            return

        if self.file.line.captured.replace(r"\\", "")[-1] == "\\":
            self.make_string_literal()
            return

        self.file.take(1)
        self.new_token("StringLiteral")

    def make_character_constant(self):
        quote = self.file.take(1)

        if self.file.next != "\\":
            char = self.file.take(1)
            self.file.take(1)
            self.new_token("CharacterConstant")

            if char == quote:
                self.warn("Empty character constant")

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
        self.new_token("CharacterConstant")

        if end_quote != quote:
            self.warn("Unterminated character constant")

        if unknown:
            self.warn("Unkown escape sequence")

    def make_operator(self):
        string = ""

        while string + self.file.next in token.OPERATOR_LIST:
            string += self.file.take(1)

        self.new_token("Operator")

    def make_include(self):
        self.check_spaces()

        if self.file.next not in "\"<":
            self.make_file_path(False)
            return

        self.file.take(1)
        lbracket = self.new_token("Punctuator")

        self.make_file_path()

        bracket = "\"" if self.file.take(1) == "\"" else "<"
        self.new_token("Punctuator")

        if lbracket.string != bracket:
            lbracket.mark()
            self.warn("Cannot mix \" \" and < > brackets in include statement")

    def make_file_path(self, terminatable = True):
        self.file.take(until = ">\"#\n")
        self.new_token("FilePath")

        if terminatable and self.file.next in "\n#":
            self.warn("Unterminated include statement")

    def make_raw_block(self):
        self.check_spaces()
        string = self.file.take(these = token.IDENTIFIER_SYMBOLS)
        self.new_token("Keyword")

        if string != "block":
            raise CompilerError("Raw code block must be followed by block keyword", self.tokens[-1])

        self.check_spaces()
        self.expecting_punctuator(":", "Raw code block must be indicted with : symbol")

        if self.file.next == "#":
            self.make_comment()

        self.expecting_punctuator("\n", "Raw code block cannot be an inline block")

        depth = self.depth
        self.at_line_start = True
        self.depth = 0

        self.check_spaces()
        first = True

        while self.depth > depth:
            string = self.file.take(until = "\n")

            if first and string == "pass":
                self.new_token("Keyword")
                self.check_spaces()
                break

            first = False
            self.new_token("Raw")
            self.check_spaces()

    def expecting_punctuator(self, symbol, message):
        line = self.file.line
        string = self.file.take(1)

        if string != symbol:
            self.tokens[-1].mark()
            raise CompilerError(message, self.tokens[-1].line)

        self.new_token("Punctuator", line)
