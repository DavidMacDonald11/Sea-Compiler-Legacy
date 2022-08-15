from lexing.token import TYPE_KEYWORDS
from .expression_statement import ExpressionStatement
from .variable_statement import VariableStatement
from ..node import Node

class Statement(Node):
    @classmethod
    def construct(cls):
        if cls.parser.next.has(*TYPE_KEYWORDS):
            return VariableStatement.construct()

        return ExpressionStatement.construct()
