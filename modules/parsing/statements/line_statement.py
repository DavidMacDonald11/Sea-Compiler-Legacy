from lexing.token import TYPE_KEYWORDS, TYPE_MODIFIER_KEYWORDS
from transpiling.statement import Statement
from .expression_statement import ExpressionStatement
from .identifier_statement import IdentifierStatement
from .assignment_statement import AssignmentStatement
from .augmented_assignment_statement import AugmentedAssignmentStatement
from .hidden_statement import HiddenStatement
from ..node import Node

class LineStatement(HiddenStatement):
    @classmethod
    def construct(cls):
        statement = LineStatementComponent.construct()
        cls.parser.expecting_has(r"\n", "EOF")

        if isinstance(statement, IdentifierStatement):
            return statement

        is_assign = isinstance(statement, AssignmentStatement)

        if is_assign and len(statement) == 1 and len(statement.expression_lists[0]) == 1:
            statement = statement.expression_lists[0].expressions[0]

        return cls(statement)

    def transpile(self):
        statement = self.statement.transpile()

        if not isinstance(statement, Statement):
            statement = Statement(statement).finish(self)

        return statement

class LineStatementComponent(Node):
    @classmethod
    def construct(cls):
        if cls.parser.next.has(*TYPE_MODIFIER_KEYWORDS, *TYPE_KEYWORDS):
            return IdentifierStatement.construct()

        if cls.parser.next.of("Identifier"):
            return AugmentedAssignmentStatement.construct()

        return ExpressionStatement.construct()
