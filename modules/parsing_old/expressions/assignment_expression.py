from lexing.token import ASSIGNMENT_OPERATOR_LIST
from ..node import Node

class AssignmentExpression(Node):
    @Node.binary_operation(ASSIGNMENT_OPERATOR_LIST, "ConditionalExpression")
    def construct(self, parser):
        pass
