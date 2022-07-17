from lexing import token
from util.warnings import CompilerError
from ..node import Node

class PrimaryExpression(Node):
    @classmethod
    def construct(cls, children):
        if children.next_token.of("Identifier", "Constant", "StringLiteral"):
            children.take()
            return cls(children)

        if children.next_token.has("(", "|"):
            lbracket = children.take()
            children.make("Expression")
            rbracket = children.expecting_has(")" if lbracket.string == "(" else "|")

            lbracket.kind = "Punctuator"
            rbracket.kind = "Punctuator"

            return cls(children)

        if children.next_token.has(*token.PRIMARY_KEYWORD_LIST):
            children.take()
            return cls(children)

        next_token = children.take()
        next_token.line.mark(next_token)
        raise CompilerError("PrimaryExpression error", children)
