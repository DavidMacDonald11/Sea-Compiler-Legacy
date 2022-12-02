from lexing.token import ASSIGNMENT_OPERATORS, FakeToken
from .assignment_statement import AssignmentStatement, ExpressionList
from .expression_statement import ExpressionStatement
from ..expressions.primary_expression import Identifier
from ..expressions.exponential_expression import ExponentialExpression
from ..expressions.multiplicative_expression import MultiplicativeExpression
from ..expressions.remainder_expression import RemainderExpression
from ..expressions.additive_expression import AdditiveExpression
from ..expressions.shift_expression import ShiftExpression
from ..expressions.bitwise_and_expression import BitwiseAndExpression
from ..expressions.bitwise_xor_expression import BitwiseXorExpression
from ..expressions.bitwise_or_expression import BitwiseOrExpression
from ..node import Node

class AugmentedAssignmentStatement(Node):
    @property
    def nodes(self) -> list:
        return [self.identifier, self.operator, self.expression]

    def __init__(self, identifier, operator, expression):
        self.identifier = identifier
        self.operator = operator
        self.expression = expression

    @classmethod
    def construct(cls):
        if not cls.parser.next.of("Identifier"):
            return ExpressionStatement.construct()

        identifier = cls.parser.take()

        if not cls.parser.next.has(*ASSIGNMENT_OPERATORS) or cls.parser.next.has("="):
            cls.parser.i -= 1
            return AssignmentStatement.construct()

        operator = cls.parser.expecting_has(*ASSIGNMENT_OPERATORS)
        return cls(identifier, operator, ExpressionStatement.construct().expression)

    def transpile(self):
        name = self.identifier.string
        operator = self.operator.string
        expression = self.expression.transpile()
        self.transpiler.symbols.at(self, name)

        op = operator[:-1]

        left = Identifier(self.identifier)
        operator = FakeToken.copy(self.operator, op)
        right = self.expression

        match op:
            case "^":
                cls = ExponentialExpression
            case "*"|"/":
                cls = MultiplicativeExpression
            case "%":
                cls = RemainderExpression
            case "+"|"-":
                cls = AdditiveExpression
            case "<<"|">>":
                cls = ShiftExpression
            case "&":
                cls = BitwiseAndExpression
            case "$":
                cls = BitwiseXorExpression
            case "|":
                cls = BitwiseOrExpression

        identifier = ExpressionList([left])
        expression = ExpressionList([cls(left, operator, right)])

        return AssignmentStatement([identifier, expression]).transpile()
