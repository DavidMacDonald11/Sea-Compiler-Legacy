from lexing import token
from util.warnings import CompilerError
from .postfix_expression import PostfixExpression
from ..node import Node

class PrimaryExpression(Node):
    def construct(self, parser):
        if parser.next.of("Identifier", "CharacterConstant", "StringLiteral"):
            parser.take()
            return self

        if parser.next.of("NumericConstant"):
            return self.construct_numeric_constant(parser)

        if parser.next.has("(", "||"):
            return self.construct_bracket(parser)

        if parser.next.has(*token.PRIMARY_KEYWORD_LIST):
            parser.take()
            return self

        error = parser.take()
        error.mark()

        message = f"PrimaryExpression error; unexpected token {error}"

        if error.of("Keyword"):
            message = f"Unexpected keyword {error.string}"

        raise CompilerError(message, parser.children)

    def construct_numeric_constant(self, parser):
        taken = parser.take()
        taken_bytes = None

        if parser.next.has("bytes"):
            taken_bytes = parser.take()

            if taken.specifier != "int":
                taken.mark()
                taken_bytes.mark()
                parser.warn("Cannot have floating number of bytes")

        if parser.next.has("i"):
            taken_i = parser.take()

            if taken_bytes is not None or parser.next.has("bytes"):
                taken_bytes = taken_bytes or parser.take()
                taken.mark()
                taken_bytes.mark()
                taken_i.mark()
                parser.warn("Cannot have an imaginary number of bytes")

        return self

    def construct_bracket(self, parser):
        lbracket = parser.take()
        parser.make("Expression")
        parser.expecting_has(")" if lbracket.has("(") else "||")

        if lbracket.has("||"):
            return self

        if parser.next.has("{", "["):
            parser.make("InitializerCompoundLiteral")
            return PostfixExpression(parser)

        return self
