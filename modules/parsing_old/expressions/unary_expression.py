from lexing.token import UNARY_OPERATOR_LIST
from ..node import Node

class UnaryExpression(Node):
    def construct(self, parser):
        if parser.next.has(*UNARY_OPERATOR_LIST):
            parser.take()
            parser.make("CastExpression")
            return self

        if parser.next.has("align", "size", "type"):
            parser.take()
            parser.expecting_has("of")
            parser.make("TypeName" if parser.next.may_be_type() else "Expression")

            return self

        if parser.next.has("dealloc", "realloc", "alloc"):
            return self.construct_alloc(parser)

        return parser.make("ExponentialExpression")

    def construct_alloc(self, parser):
        keyword = parser.take()

        if not keyword.has("alloc"):
            parser.make("Expression")

        if keyword.has("dealloc"):
            return self

        if keyword.has("realloc"):
            parser.expecting_has("to")

        parser.make("TypeName" if parser.next.may_be_type() else "Expression")

        if parser.next.has("with"):
            parser.take()
            parser.make("Expression")

        self.specifier = "Alloc"
        return self
