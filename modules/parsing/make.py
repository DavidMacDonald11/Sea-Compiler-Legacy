from .expressions.primary_expression import PrimaryExpression

CLASSES = (
    PrimaryExpression,
)

CONSTRUCT_MAP = {cls.__name__: cls.construct for cls in CLASSES}
