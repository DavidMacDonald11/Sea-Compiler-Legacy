from ..node import Node
from .postfix_expression import PostfixExpression

class CastExpression(Node):
    def construct(self, parser):
        if not parser.next.has("("):
            return parser.make("UnaryExpression")

        parser.ignore()

        if not parser.next.may_be_type():
            parser.unignore()
            return self

        parser.take_previous()
        parser.make("TypeName")
        parser.expecting_has(")")

        if parser.next.has("[", "{"):
            parser.make("InitializerCompoundLiteral")
            return PostfixExpression(parser)

        parser.make("CastExpression")
        return self
