from .expressions.primary_expression import PrimaryExpression
from .expressions.postfix_expression import PostfixExpression
from .statements.statement import Statement
from .statements.file_statement import FileStatement

CLASSES = (
    PrimaryExpression,
    PostfixExpression,
    Statement,
    FileStatement
)

CONSTRUCT_MAP = {cls.__name__: cls.construct for cls in CLASSES}
CONSTRUCT_MAP["Expression"] = PostfixExpression.construct
CONSTRUCT_MAP["AssignmentExpression"] = CONSTRUCT_MAP["Expression"]
