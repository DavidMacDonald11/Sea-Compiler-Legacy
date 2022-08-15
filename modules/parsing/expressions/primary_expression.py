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
            return (f"{self.token.specifier}64", self.token.string)

        return ("c64", f"{self.token.string}j")

class CharacterConstant(PrimaryNode):
    def transpile(self):
        return ("u64", self.token.string)

class Identifier(PrimaryNode):
    def transpile(self):
        name = self.token.string
        var = self.transpiler.symbols[name]

        if var is None:
            self.transpiler.warnings.error(self, f"Reference to undeclared variable '{name}'")
            return ("cmax", f"/*{name}*/")

        e_type, _ = self.transpiler.c_type(var.s_type)

        if var.s_type in ("imag32", "imag64", "imag"):
            return (e_type, f"({var.c_name} * 1.0j)")

        return (e_type, var.c_name)

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
        e_type, expression = self.expression.transpile()
        return (e_type, f"({expression})")

class NormExpression(ParenthesesExpression):
    wrote = []

    @classmethod
    def construct(cls):
        cls.parser.expecting_has("||")
        node = cls(cls.parser.expression.construct())
        cls.parser.expecting_has("||")
        return node

    def transpile(self):
        e_type, expression = self.expression.transpile()

        match e_type:
            case "bool":
                return ("u64", f"({expression})")
            case "u64"|"umax":
                return (e_type, f"({expression})")
            case "i64"|"imax":
                func = self.write_generic_func(e_type)
                return ("umax", f"({func}({expression}))")
            case "f64":
                self.transpiler.include("math")
                return (e_type, f"(fabs({expression}))")
            case "c64":
                self.transpiler.include("complex")
                return ("f64", f"(cabs({expression}))")
            case "fmax"|"cmax":
                self.transpiler.include("complex")
                return ("fmax", f"(cabsl({expression}))")

    def write_generic_func(self, e_type):
        func = f"__sea_func_norm_{e_type}__"

        if func in type(self).wrote: return func
        type(self).wrote += [func]

        e_type = self.transpiler.safe_type(e_type)

        self.transpiler.header("\n".join((
            f"{e_type} {func}({e_type} num)", "{",
            "\treturn (num < 0) ? -num : num; ", "}\n"
        )))

        return func

class PrimaryKeyword(PrimaryNode):
    def transpile(self):
        return ("bool", "1" if self.token.has("True") else "0")
