from .expression_statement import ExpressionStatement
from ..node import Node

class Statement(Node):
    @classmethod
    def construct(cls):
        return ExpressionStatement.construct()
