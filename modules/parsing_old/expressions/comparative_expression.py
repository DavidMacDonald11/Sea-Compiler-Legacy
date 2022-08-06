from lexing.token import COMPARATIVE_OPERATOR_LIST
from ..node import Node

class ComparativeExpression(Node):
    OPERATORS = ["is", "in", "not"] + list(COMPARATIVE_OPERATOR_LIST)

    @Node.binary_operation(OPERATORS, "BitwiseOrExpression")
    def construct(self, parser):
        if parser.next.has("in", "not"):
            parser.next.mark()
            parser.warn(f"Cannot use {parser.next.string} alone in ComparativeExpression")
            return

        if parser.next.has("is"):
            parser.take()

            if parser.next.has("not"):
                parser.take()

            if parser.next.has("in"):
                parser.take()
            elif parser.next.has("defined"):
                parser.take()
                parser.expecting_has("as")

            parser.untake()
