from ..node import Node

class StaticAssertStatement(Node):
    @classmethod
    def construct(cls, children):
        children.take()
        children.make("ConstantExpression")
        children.expecting_has("else")
        children.expecting_of("StringLiteral")
        children.expecting_line_end()

        return cls(children)
