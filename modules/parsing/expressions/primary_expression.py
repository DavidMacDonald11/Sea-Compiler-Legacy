import re
from lexing.token import PRIMARY_KEYWORDS
from transpiling.expression import Expression
from transpiling.utils import util, new_util
from ..node import Node, PrimaryNode

class PrimaryExpression(Node):
    @classmethod
    def construct(cls):
        if cls.parser.next.of("NumericConstant"):
            return NumericConstant.construct()

        if cls.parser.next.of("CharacterConstant"):
            return CharacterConstant.construct()

        if cls.parser.next.of("StringConstant"):
            return StringConstant.construct()

        if cls.parser.next.of("Identifier"):
            return Identifier.construct()

        if cls.parser.next.has("["):
            return ArrayList.construct()

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
        specifier = "nat" if self.token.specifier == "i" else "real"
        string = self.convert_base(self.token.string)

        if len(self.nodes) == 1:
            return Expression(f"{specifier}64", string)

        return Expression("imag64", f"{string}j")

    def convert_base(self, string):
        if "e" not in string:
            if "b" not in string:
                return str(int(string)) if self.token.specifier == "i" else str(float(string))

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
        return Expression("char", self.token.raw_string)

class StringConstant(PrimaryNode):
    @classmethod
    def construct(cls):
        tokens = [cls.parser.take()]

        if '"""' not in tokens[0].string:
            return cls(*tokens)

        while cls.parser.next.of("StringConstant"):
            tokens += [cls.parser.take()]
            if re.match(r'(?<!\\)"""', tokens[-1].string) is not None: break

        return cls(*tokens)

    def transpile(self):
        prefix = self.token.string[0]
        prefix = "" if prefix == '"' else prefix

        if prefix != "":
            raise NotImplementedError("String prefixes cannot be transpiled (yet)")

        string = self.token.raw_string

        if len(self.tokens) > 0:
            string = (string + "".join(t.raw_string for t in self.tokens))
            string = re.sub(r'(?<!\\)"""', '"', string)
            string = re.sub(r'(?<!\\)\\"', '"', string)
            string = re.sub(r'(?<!^)"(?!$)', r'\"', string)
            string = re.sub(r"\n", " \\\n", string)
            string = re.sub(r"\t", "\t", string)

        self.transpiler.include("string")
        return self.transpiler.cache_new_temp_str(Expression("str", string))

class Identifier(PrimaryNode):
    def transpile(self):
        name = self.token.string
        var = self.transpiler.symbols.at(self, name)
        expression = var.access(self)

        if "imag" in var.kind and not self.transpiler.context.in_ownership:
            return expression.add("(", " * 1.0j)")

        return expression

# TODO array ranges
# TODO array generators
# TODO "is" expression
# TODO "in" expression
# TODO ownership splits
# TODO array element assignment

class ArrayList(Node):
    @property
    def imag(self):
        if self.transpiler.context.array is None:
            return False

        return "imag" in self.transpiler.context.array.kind

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

    def transpile(self):
        left = self.expressions[0].transpile().operate(self, arrays = True)

        if self.imag:
            left.drop_imaginary(self, any_kind = True)

        for expression in self.expressions[1:]:
            right = expression.transpile().operate(self, arrays = True)

            if self.imag:
                right.drop_imaginary(self, any_kind = True)

            self.verify_next(left, right)

            left = Expression.resolve(left, right, True, True).new(f"{left}")
            left.add(after = f", {right}")

        left.arrays += 1
        left.add("{", "}")

        self.verify_string_array(left, self.transpiler.context.array)
        return self.transpiler.cache_new_temp_array(left, len(self.expressions))

    def verify_string_array(self, left, array):
        if array is None:
            return

        if array.kind == "str" and left.kind != "str":
            self.transpiler.warnings.error(self, "Cannot assign str array to non-str array")
        elif array.kind != "str" and left.kind == "str":
            self.transpiler.warnings.error(self, "Cannot assign non-str array to str array")

    def verify_next(self, left, right):
        if left.kind != "str" and right.kind == "str":
            self.transpiler.warnings.error(self, "Cannot have str in non-str array")
        elif left.kind == "str" and right.kind != "str":
            self.transpiler.warnings.error(self, "Cannot have non-str in str array")

        if left.arrays != right.arrays:
            self.transpiler.warnings.error(self, "Mismatching array element dimensions")

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
        return self.expression.transpile().add("(", ")")

class NormExpression(ParenthesesExpression):
    @classmethod
    def construct(cls):
        cls.parser.expecting_has("||")
        node = cls(cls.parser.expression.construct())
        cls.parser.expecting_has("||")
        return node

    def transpile(self):
        if isinstance(self.expression, NormExpression):
            return self.expression.transpile()

        expression = self.expression.transpile().operate(self).add("(", ")")
        kind = expression.kind

        if kind in ("bool", "char"):
            return expression.cast("nat8")

        if "nat" in kind:
            return expression

        if "int" in kind:
            func = util(self.util_norm("int" if kind == "int" else "int64"))
            return expression.add(f"({func}", ")").cast("nat")

        if kind in ("real32", "real64"):
            self.transpiler.include("math")
            return expression.add("(fabs", ")").cast("real")

        if kind in ("imag32", "imag64", "cplex32", "cplex64"):
            self.transpiler.include("complex")
            return expression.add("(cabs", ")").cast("real32" if "32" in kind else "real64")

        if kind in ("real", "imag", "cplex"):
            self.transpiler.include("complex")
            return expression.add("(cabsl", ")").cast("real")

        raise NotImplementedError(f"NormExpression of {kind}")

    @staticmethod
    def util_norm(kind):
        name = f"norm_{kind}"

        @new_util(name)
        def func(func):
            return "\n".join((
                f"__sea_type_{kind}__ {func}({kind} num)", "{",
                "\treturn (num < 0) ? -num : num; ", "}\n"
            ))

        return name

class PrimaryKeyword(PrimaryNode):
    def transpile(self):
        return Expression("bool", "1" if self.token.has("True") else "0")
