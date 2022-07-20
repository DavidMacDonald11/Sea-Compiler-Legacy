from ..node import Node

class StaticAssertStatement(Node):
    @classmethod
    def construct(cls, children):
        children.take()
        children.make("ConstantExpression")
        children.expecting_has("else")
        children.expecting_of("StringLiteral")

        children.take_comments()
        children.expecting_has("\n", "")
        children.ignore_format_tokens()

        return cls(children)
