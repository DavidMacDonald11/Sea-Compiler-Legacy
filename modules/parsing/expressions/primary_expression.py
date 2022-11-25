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
        specifier = self.token.specifier
        string = self.convert_base(self.token.string)

        if len(self.nodes) == 1:
            return self.transpiler.expression(f"{specifier}64", string)

        return self.transpiler.expression("g64", f"{string}j")

    def convert_base(self, string):
        if "e" not in string:
            if "b" not in string:
                return str(int(string))

            return self.convert_to_base(*string.split("b"))

        digits, power = string.split("e")

        if "b" in power:
            power = self.convert_to_base(*power.split("b"), decimal = True)

        if "b" in digits:
            base, digits = digits.split("b")
            digits = self.convert_to_base(base, digits, decimal = True)
            digits = str(float(digits) * int(base) ** float(power))

        return digits

    def convert_to_base(self, base, digits, decimal = False):
        if digits[0] in "+-":
            sign = digits[0]
            digits = digits[1:]
        else:
            sign = ""

        if "." in digits:
            return sign + self.convert_float_to_base(int(base), digits)

        return sign + self.convert_int_to_base(int(base), digits, decimal)

    def convert_int_to_base(self, base, digits, decimal = False):
        try:
            if base < 2: raise ValueError()

            if decimal:
                return str(int(digits, base))

            return f"0x{hex(int(digits, base))[2:].upper()}"
        except ValueError:
            self.transpiler.warnings.error(self, "Numeric base must be between 2 and 36")
            return digits

    def convert_float_to_base(self, base, digits):
        integer, floats = f"0{digits}".split(".")

        value = sum(int(digit, base) * base ** -(i + 1) for i, digit in enumerate(floats))
        value += int(self.convert_int_to_base(base, integer, decimal = True))

        return str(value)

class CharacterConstant(PrimaryNode):
    def transpile(self):
        return self.transpiler.expression("u64", self.token.string)

class Identifier(PrimaryNode):
    def transpile(self):
        name = self.token.string
        var = self.transpiler.symbols.at(self, name)

        if var is None:
            return self.transpiler.expression("cmax", f"/*{name}*/")

        expression = var.access(self, self.transpiler.expression())
        expression.identifiers += [name]

        if var.s_type in ("imag32", "imag64", "imag"):
            expression.cast("g64" if var.s_type in ("imag32", "imag64") else "gmax")

            if self.transpiler.context.in_ownership:
                return expression

            return expression.new("(%s * 1.0j)")

        return expression

class ExpressionList(Node):
    @property
    def nodes(self) -> list:
        return self.expressions

    def __init__(self, expressions):
        self.expressions = expressions

    @classmethod
    def construct(cls):
        cls.parser.expecting_has("[")
        cls.parser.ignore_spaces()

        expressions = [cls.parser.expression.construct()]

        while cls.parser.next.has(","):
            cls.parser.take()
            cls.parser.ignore_spaces()

            if cls.parser.next.has("]"): break
            expressions += [cls.parser.expression.construct()]

        cls.parser.ignore_spaces()
        cls.parser.expecting_has("]")
        return cls(expressions)

    # TODO allow x,y = [1,2] if True else [3,4] or x, y = [1, 2] + [3, 4]
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
            case "g64"|"c64":
                self.transpiler.include("complex")
                return expression.new("(cabs(%s))").cast("f64")
            case "fmax"|"gmax"|"cmax":
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
