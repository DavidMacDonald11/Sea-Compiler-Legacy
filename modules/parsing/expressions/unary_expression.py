from lexing.token import UNARY_OPERATOR_LIST
from ..node import Node

class UnaryExpression(Node):
    @classmethod
    def construct(cls, children):
        if children.next_token.has(*UNARY_OPERATOR_LIST):
            children.take()
            children.make("CastExpression")
            return cls(children)

        if children.next_token.has("align", "size", "type"):
            children.take()
            children.expecting_has("of")

            if children.next_token_may_be_type:
                children.make("TypeName")
            else:
                children.make("Expression")

            return cls(children)

        if children.next_token.has("dealloc", "realloc", "alloc"):
            keyword = children.take()

            if not keyword.has("alloc"):
                children.make("Expression")

            if keyword.has("dealloc"):
                return cls(children)

            if keyword.has("realloc"):
                children.expecting_has("to")

            if children.next_token_may_be_type:
                children.make("TypeName")
            else:
                children.make("Expression")

            if children.next_token.has("as"):
                children.take()
                children.make("Expression")

            return cls(children)

        return children.make("ExponentialExpression")
