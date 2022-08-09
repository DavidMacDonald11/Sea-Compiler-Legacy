from ..node import Node, PrimaryNode

class PrimaryExpression(Node):
    @classmethod
    def construct(cls):
        if cls.parser.next.of("NumericConstant"):
            return NumericConstant.construct()

        if cls.parser.next.has("("):
            return ParenthesesExpression.construct()

        if cls.parser.next.has("||"):
            return NormExpression.construct()

        failure = cls.parser.take()
        message = f"PrimaryExpression error; unexpected token {failure}"
        raise cls.parser.warnings.fail(failure, message)

class NumericConstant(PrimaryNode):
    @classmethod
    def construct(cls):
        return cls(cls.parser.take())

    def transpile(self, transpiler):
        transpiler.expression_type = f"{self.token.specifier[0]}64"
        return self.token.string

class ParenthesesExpression(Node):
    @property
    def nodes(self) -> list:
        return [self.expression]

    def __init__(self, expression):
        self.expression = expression

    @classmethod
    def construct(cls):
        cls.parser.expecting_has("(")
        node = cls(cls.parser.expression.construct())
        cls.parser.expecting_has(")")
        return node

    def transpile(self, transpiler):
        return f"({self.expression.transpile(transpiler)})"

class NormExpression(ParenthesesExpression):
    @classmethod
    def construct(cls):
        cls.parser.expecting_has("||")
        node = cls(cls.parser.expression.construct())
        cls.parser.expecting_has("||")
        return node

    def transpile(self, transpiler):
        expression = self.expression.transpile(transpiler)

        if transpiler.expression_type == "u64":
            return expression

        transpiler.include("math")
        cast = "" if transpiler.expression_type != "i64" else "(i64)"

        return f"({cast}fabs({expression}))"
