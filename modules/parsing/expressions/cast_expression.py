from .bitwise_or_expression import BitwiseOrExpression
from ..declarations.type_keyword import TypeKeyword
from ..node import Node

class CastExpression(Node):
    @property
    def nodes(self) -> list:
        return [self.expression, self.type_keyword]

    def __init__(self, expression, type_keyword):
        self.expression = expression
        self.type_keyword = type_keyword

    @classmethod
    def construct(cls):
        expression = BitwiseOrExpression.construct()

        while cls.parser.next.has("as"):
            cls.parser.take()
            expression = cls(expression, TypeKeyword.construct())

        return expression

    def transpile(self):
        expression = self.expression.transpile()
        kind = self.type_keyword.token.string

        if expression.kind == kind:
            return expression

        expression.operate(self)

        if kind == "bool":
            return expression.add("(", " != 0)").cast("bool")

        if kind == "str":
            return self.transpile_str(expression)

        keyword = self.type_keyword.transpile()

        if "imag" not in kind:
            return expression.add(f"({keyword})(", ")").cast(kind)

        self.transpiler.include("complex")
        suffix = "f" if "32" in kind else ("" if "64" in kind else "l")
        return expression.add(f"(cimag{suffix}(", ") * 1.0j)").cast(kind)

    def transpile_str(self, expression):
        self.transpiler.include("stdio")
        format_tag = expression.format_tag

        if expression.kind == "bool":
            expression.add("(", ') ? "True" : "False"').cast("str")
        elif "imag" in expression.kind:
            expression.drop_imaginary(self).cast(expression.kind.replace("imag", "real"))
            format_tag = f"{format_tag}i"
        elif "cplex" in expression.kind:
            expression, format_tag = self.transpile_str_cplex(expression, format_tag)

        if "cplex" not in expression.kind:
            expression = self.transpiler.cache_new_temp(expression)

        expression.add(f'"{format_tag}", ').cast("str")
        return self.transpiler.cache_new_temp(expression, buffer = True)

    def transpile_str_cplex(self, expression, format_tag):
        expression = self.transpiler.cache_new_temp(expression)
        kind, string = expression.kind, expression.string

        self.transpiler.include("complex")
        suffix = "f" if "32" in kind else ("" if "64" in kind else "l")
        expression.new(f"creal{suffix}({string}), cimag{suffix}({string})")
        format_tag = f"{format_tag} + {format_tag}i"

        return expression, format_tag
