from lexing.token import COMPARATIVE_OPERATOR_LIST
from ..node import Node

class ComparativeExpression(Node):
    OPERATORS = ["is", "in", "not"] + list(COMPARATIVE_OPERATOR_LIST)

    @Node.binary_operation(OPERATORS, "BitwiseOrExpression")
    def construct(self, parser):
        if parser.next.has("is"):
            parser.ignore()

            if parser.next.has("not"):
                parser.take_previous()
                return

            parser.unignore()
            return

        if parser.next.has("not"):
            parser.ignore()

            if parser.next.has("in"):
                parser.take_previous()
                return

            parser.unignore()
            parser.next.mark()
            parser.warn("Cannot use not operator alone in ComparativeExpression")
