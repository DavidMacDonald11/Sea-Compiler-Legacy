from util.misc import is_integer
from transpiling.expression import Expression
from .unary_expression import UnaryExpression
from ..node import BinaryOperation

class MultiplicativeExpression(BinaryOperation):
    wrote = []

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

        size_func = type(self).write_size_func(self.transpiler)
        cast = "(__sea_type_nat__)" if "nat" in right.kind else ""
        size = f"{size_func}({left}, {cast}({right}))"

        result = self.transpiler.cache_new_temp_array(Expression("str"), size, string = True)
        func = type(self).write_str_multiply_func(self.transpiler)
        result.add(f"{func}(", f", {left})")

        return self.transpiler.cache_new_temp(result)

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

        size_func = type(self).write_size_func(self.transpiler)
        cast = "(__sea_type_nat__)" if "nat" in right.kind else ""
        size = f"{size_func}({left}, {cast}(({right} == 0) ? 1 : {right}))"

        result = Expression(left.kind, "", left.arrays)
        result = self.transpiler.cache_new_temp_array(result, size, string = True)

        kind = left.kind if left.kind != "str" and left.arrays < 2 else "array"
        func = type(self).write_array_multiply_func(self.transpiler, kind)
        result.add(f"{func}(", f", {left})")

        print(result.arrays, result.kind)

        return self.transpiler.cache_new_temp(result)

    @classmethod
    def write_size_func(cls, transpiler):
        func = "__sea_func_array_mul_size__"
        if func in cls.wrote: return func
        cls.wrote += [func]

        transpiler.header("\n".join((
            f"#define {func}(ARR, MUL) (_Generic((MUL), __sea_type_nat__: MUL, \\",
            "\tdefault: (MUL < 0) ? 0 : MUL) * ARR.size)"
        )))

        return func

    @classmethod
    def write_str_multiply_func(cls, transpiler):
        func = "__sea_func_str_mul__"
        if func in cls.wrote: return func
        cls.wrote += [func]

        array = "__sea_type_array__"
        kind = "__sea_type_str__"

        transpiler.header("\n".join((
            f"{array} {func}({array} out, {array} in)", "{",
            "\tfor(__sea_type_nat__ i = 0; i < out.size; i++)", "\t{",
            f"\t\t(({kind})out.data)[i] = (({kind})in.data)[i % in.size];", "\t}",
            f"\t(({kind})out.data)[out.size] = '\\0';",
            "\treturn out;", "}"
        )))

        return func

    @classmethod
    def write_array_multiply_func(cls, transpiler, kind):
        func = f"__sea_func_array_mul_{kind}__"
        if func in cls.wrote: return func
        cls.wrote += [func]

        array = "__sea_type_array__"
        kind = f"__sea_type_{kind}__"

        transpiler.header("\n".join((
            f"{array} {func}({array} out, {array} in)", "{",
            "\tfor(__sea_type_nat__ i = 0; i < out.size; i++)", "\t{",
            f"\t\t(({kind} *)out.data)[i] = (({kind} *)in.data)[i % in.size];", "\t}",
            "\treturn out;", "}"
        )))

        return func
