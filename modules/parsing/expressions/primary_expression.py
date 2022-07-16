from ..node import Node

class PrimaryExpression(Node):
    @classmethod
    def construct(cls, parser):
        if parser.token.of("Identifier", "Constant", "StringLiteral"):
            parser.take()
            return parser.new_node(cls)
