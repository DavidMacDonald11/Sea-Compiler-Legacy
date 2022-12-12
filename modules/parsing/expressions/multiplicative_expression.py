from util.misc import is_integer
from transpiling.expression import Expression
from transpiling.utils import util, new_util
from .unary_expression import UnaryExpression
from ..node import BinaryOperation

class MultiplicativeExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["*", "/"], UnaryExpression)

    def transpile(self):
        operator = self.operator.string

        left = self.left.transpile().operate(self, arrays = (operator == "*"))
        right = self.right.transpile().operate(self, arrays = (operator == "*"))

        if left.arrays > 0 or right.arrays > 0:
            return self.transpile_array(left, right)

        if left.kind == "str" or right.kind == "str":
            return self.transpile_str(left, right)

        result = Expression.resolve(left, right).cast_up()
        result.new(f"{left} {operator} {right}")

        return result

    def transpile_str(self, left, right):
        message = "Can only multiply str with int or nat"

        if left.kind == right.kind:
            self.transpiler.warnings.error(self, message)
        elif left.kind != "str" and not is_integer(left):
            self.transpiler.warnings.error(self, message)
        elif right.kind != "str" and not is_integer(right):
            self.transpiler.warnings.error(self, message)

        if left.kind != "str":
            right, left = left, right

        size_func = util("array_multiply_size")
        cast = "(__sea_type_nat__)" if "nat" in right.kind else ""
        size = f"{size_func}({left}, {cast}({right}))"

        result = self.transpiler.temps.cache_new_array(Expression("str"), size, string = True)
        func = util("str_multiply")
        result.add(f"{func}(", f", {left})")

        return self.transpiler.temps.cache_new(result)

    def transpile_array(self, left, right):
        message = "Can only multiply array with int or nat"

        if left.arrays > 0 and right.arrays > 0:
            self.transpiler.warnings.error(self, message)
        elif left.arrays == 0 and not is_integer(left):
            self.transpiler.warnings.error(self, message)
        elif right.arrays == 0 and not is_integer(right):
            self.transpiler.warnings.error(self, message)

        if left.arrays == 0:
            right, left = left, right

        size_func = util("array_multiply_size")
        cast = "(__sea_type_nat__)" if "nat" in right.kind else ""
        size = f"{size_func}({left}, {cast}(({right} == 0) ? 1 : {right}))"

        result = Expression(left.kind, "", left.arrays)
        result = self.transpiler.temps.cache_new_array(result, size, string = True)

        kind = left.kind if left.kind != "str" and left.arrays < 2 else "array"
        func = util(self.util_array_multiply(kind))
        result.add(f"{func}(", f", {left})")

        print(result.arrays, result.kind)

        return self.transpiler.temps.cache_new(result)

    @new_util("array_multiply_size")
    @staticmethod
    def util_array_multiply_size(func):
        return "\n".join((
            f"#define {func}(ARR, MUL) (_Generic((MUL), __sea_type_nat__: MUL, \\",
            "\tdefault: (MUL < 0) ? 0 : MUL) * ARR.size)"
        ))

    @new_util("str_multiply")
    @staticmethod
    def util_str_multiply(func):
        array = "__sea_type_array__"
        kind = "__sea_type_str__"

        return "\n".join((
            f"{array} {func}({array} out, {array} in)", "{",
            "\tfor(__sea_type_nat__ i = 0; i < out.size; i++)", "\t{",
            f"\t\t(({kind})out.data)[i] = (({kind})in.data)[i % in.size];", "\t}",
            f"\t(({kind})out.data)[out.size] = '\\0';",
            "\treturn out;", "}"
        ))

    @staticmethod
    def util_array_multiply(kind):
        name = "array_multiply"

        array = "__sea_type_array__"
        kind = f"__sea_type_{kind}__"

        @new_util(name)
        def func(func):
            return "\n".join((
                f"{array} {func}({array} out, {array} in)", "{",
                "\tfor(__sea_type_nat__ i = 0; i < out.size; i++)", "\t{",
                f"\t\t(({kind} *)out.data)[i] = (({kind} *)in.data)[i % in.size];", "\t}",
                "\treturn out;", "}"
            ))

        return name
