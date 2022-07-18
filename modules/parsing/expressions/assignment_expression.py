from lexing.token import ASSIGNMENT_OPERATOR_LIST
from ..node import Node, binary_operation

class AssignmentExpression(Node):
    @classmethod
    @binary_operation(ASSIGNMENT_OPERATOR_LIST, "ConditionalExpression")
    def construct(cls, children):
        pass
