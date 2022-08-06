from ..node import Node

class StaticAssertStatement(Node):
    def construct(self, parser):
        parser.take()
        parser.make("ConstantExpression")
        parser.expecting_has("else")
        parser.expecting_of("StringLiteral")
        parser.expecting_line_end()

        return self
