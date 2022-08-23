from lexing.token import PRIMARY_KEYWORDS
from ..node import Node, PrimaryNode

class PrimaryExpression(Node):
    @classmethod
    def construct(cls):
        if cls.parser.next.of("NumericConstant"):
            return NumericConstant.construct()

        if cls.parser.next.of("CharacterConstant"):
            return CharacterConstant.construct()

        if cls.parser.next.of("Identifier"):
            return Identifier.construct()

        if cls.parser.next.has("["):
            return ExpressionList.construct()

        if cls.parser.next.has("("):
            return ParenthesesExpression.construct()

        if cls.parser.next.has("||"):
            return NormExpression.construct()

        if cls.parser.next.has(*PRIMARY_KEYWORDS):
            return PrimaryKeyword.construct()

        failure = cls.parser.take()
        message = f"PrimaryExpression error; unexpected token {failure}"
        raise cls.parser.warnings.fail(failure, message)

class NumericConstant(PrimaryNode):
    @classmethod
    def construct(cls):
        num = cls.parser.take()
        return cls(num, cls.parser.take()) if cls.parser.next.has("i") else cls(num)

    def transpile(self):
        if len(self.nodes) == 1:
            return self.transpiler.expression(f"{self.token.specifier}64", self.token.string)

        return self.transpiler.expression("c64", f"{self.token.string}j")

class CharacterConstant(PrimaryNode):
    def transpile(self):
        return self.transpiler.expression("u64", self.token.string)

class Identifier(PrimaryNode):
    def transpile(self):
        name = self.token.string
        var = self.transpiler.symbols.at(self, name)

        if var is None:
            return self.transpiler.expression("cmax", f"/*{name}*/")

        c_name = var.access(self)

        if var.s_type in ("imag32", "imag64", "imag"):
            return self.transpiler.expression(None, f"({c_name} * 1.0j)").cast(var.s_type)

        return self.transpiler.expression(None, f"{c_name}").cast(var.s_type)

class ExpressionList(Node):
    @property
    def nodes(self) -> list:
        return self.expressions

    def __init__(self, expressions):
        self.expressions = expressions

    @classmethod
    def construct(cls):
        cls.parser.expecting_has("[")
        expressions = [cls.parser.expression.construct()]

        while cls.parser.next.has(","):
            cls.parser.take()
            if cls.parser.next.has("]"): break
            expressions += [cls.parser.expression.construct()]

        cls.parser.expecting_has("]")
        return cls(expressions)

    def transpile(self):
        expression = self.transpiler.expression("list", f"{self.expressions[0].transpile()}")

        for exp in self.expressions[1:]:
            expression.new(f"%s, {exp.transpile()}")

        return expression.new("/*{%s}*/")

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

    def transpile(self):
        return self.expression.transpile().new("(%s)")

class NormExpression(ParenthesesExpression):
    wrote = []

    @classmethod
    def construct(cls):
        cls.parser.expecting_has("||")
        node = cls(cls.parser.expression.construct())
        cls.parser.expecting_has("||")
        return node

    def transpile(self):
        if isinstance(self.expression, NormExpression):
            return self.expression.transpile()

        expression = self.expression.transpile().operate(self)

        match expression.e_type:
            case "bool":
                return expression.new("(%s)").cast("u64")
            case "u64"|"umax":
                return expression.new("(%s)")
            case "i64"|"imax":
                func = self.write_generic_func(expression)
                return expression.new(f"({func}(%s))").cast("umax")
            case "f64":
                self.transpiler.include("math")
                return expression.new("(fabs(%s))")
            case "c64":
                self.transpiler.include("complex")
                return expression.new("(cabs(%s))").cast("f64")
            case "fmax"|"cmax":
                self.transpiler.include("complex")
                return expression.new("(cabsl(%s))").cast("fmax")

    def write_generic_func(self, expression):
        func = f"__sea_func_norm_{expression.e_type}__"

        if func in type(self).wrote: return func
        type(self).wrote += [func]

        e_type = expression.c_type

        self.transpiler.header("\n".join((
            f"{e_type} {func}({e_type} num)", "{",
            "\treturn (num < 0) ? -num : num; ", "}\n"
        )))

        return func

class PrimaryKeyword(PrimaryNode):
    def transpile(self):
        return self.transpiler.expression("bool", "1" if self.token.has("True") else "0")
