from .expressions.primary_expression import PrimaryExpression
from .statements.statement import Statement
from .statements.file_statement import FileStatement

CLASSES = (
    PrimaryExpression,
    Statement,
    FileStatement
)

CONSTRUCT_MAP = {cls.__name__: cls.construct for cls in CLASSES}
CONSTRUCT_MAP["Expression"] = PrimaryExpression.construct
