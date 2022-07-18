from lexing import token
from util.warnings import CompilerError
from ..node import Node

class PrimaryExpression(Node):
    @classmethod
    def construct(cls, children):
        if children.next_token.of("Identifier", "Constant", "StringLiteral"):
            taken = children.take()
            taken_bytes = None

            if children.next_token.has("bytes"):
                taken_bytes = children.take()

                if not (taken.of("NumericConstant") and taken.specifier == "int"):
                    taken.mark()
                    taken_bytes.mark()
                    children.warn("Cannot use bytes keyword on non-integer")

            if children.next_token.has("i"):
                taken_i = children.take()

                if not taken.of("NumericConstant"):
                    taken.mark()
                    taken_i.mark()
                    children.warn("Can only use the imaginary with NumericConstants")

                if taken_bytes is not None or children.next_token.has("bytes"):
                    taken_bytes = taken_bytes or children.take()
                    taken_bytes.mark()
                    children.warn("Cannot have an imaginary number of bytes")

            return cls(children)

        if children.next_token.has("(", "||"):
            lbracket = children.take()
            children.make("Expression")
            children.expecting_has(")" if lbracket.string == "(" else "||")

            return cls(children)

        if children.next_token.has(*token.PRIMARY_KEYWORD_LIST):
            children.take()
            return cls(children)

        error = children.take()
        error.mark()

        message = f"PrimaryExpression error; unexpected token {error}"

        if error.of("Keyword"):
            message = f"Unexpected keyword {error.string}"

        raise CompilerError(message, children)
