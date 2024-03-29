from lexing.token import TYPE_KEYWORDS, TYPE_MODIFIER_KEYWORDS
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
        return statement if isinstance(statement, IdentifierStatement) else cls(statement)

class LineStatementComponent(Node):
    @classmethod
    def construct(cls):
        if cls.parser.next.has(*TYPE_MODIFIER_KEYWORDS, *TYPE_KEYWORDS):
            return IdentifierStatement.construct()

        if cls.parser.next.of("Identifier"):
            statement = AugmentedAssignmentStatement.construct()

            if isinstance(statement, AssignmentStatement) and len(statement.expression_lists) == 1:
                statement = statement.expression_lists[0].to_expression_statement()

            return statement

        return ExpressionStatement.construct()
