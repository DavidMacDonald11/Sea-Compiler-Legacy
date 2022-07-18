from lexing.token import COMPARATIVE_OPERATOR_LIST
from ..node import Node, binary_operation

class ComparativeExpression(Node):
    OPERATORS = ["is", "in", "not"] + list(COMPARATIVE_OPERATOR_LIST)

    @classmethod
    @binary_operation(OPERATORS, "BitwiseOrExpression")
    def construct(cls, children):
        if children.next_token.has("is"):
            children.ignore()

            if children.next_token.has("not"):
                children.take_previous()
                return

            children.unignore()
            return

        if children.next_token.has("not"):
            children.ignore()

            if children.next_token.has("in"):
                children.take_previous()
                return

            children.unignore()
            children.next_token.mark()
            children.warn("Cannot use not operator alone in ComparativeExpression")
