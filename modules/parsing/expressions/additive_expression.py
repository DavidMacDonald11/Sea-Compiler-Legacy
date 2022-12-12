from transpiling.expression import Expression
from transpiling.utils import util, new_util
from .multiplicative_expression import MultiplicativeExpression
from ..node import BinaryOperation

class AdditiveExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["+", "-"], MultiplicativeExpression)

    def transpile(self):
        operator = self.operator.string

        left = self.left.transpile().operate(self, arrays = (operator == "+"))
        right = self.right.transpile().operate(self, arrays = (operator == "+"))

        if left.arrays > 0 or right.arrays > 0:
            return self.transpile_array(left, right)

        if left.kind == "str" or right.kind == "str":
            return self.transpile_str(left, right)

        result = Expression.resolve(left, right).cast_up()
        result.new(f"{left} {operator} {right}")

        return result

    def transpile_str(self, left, right):
        if left.arrays != right.arrays:
            self.transpiler.warnings.error(self, "Cannot add str and arrays")

        if left.kind == "str" and right.kind not in ("char", "str"):
            self.transpiler.warnings.error(self, "Can only add str and char values to str")
        elif right.kind == "str" and left.kind not in ("char", "str"):
            self.transpiler.warnings.error(self, "Can only add str and char values to str")

        r_size = f"{right}.size" if (right.kind == "str") else "1"
        l_size = f"{left}.size" if (left.kind == "str") else "1"
        append = util("str_append")

        result = Expression.resolve(left, right, True, True).cast_up()
        self.transpiler.temps.cache_new_array(result, f"{r_size} + {l_size}", string = True)

        l_cast = "" if left.kind == "str" else "(__sea_type_char__)"
        r_cast = "" if right.kind == "str" else "(__sea_type_char__)"
        result.add(f"{append}(", f", {l_cast}({left}), {r_cast}({right}))")

        return self.transpiler.temps.cache_new(result)

    @new_util("str_append")
    @staticmethod
    def util_str_append(func):
        helper = "__sea_hutil_str_append"
        kind = "__sea_type_array__"

        return "\n".join((
            f"{kind} {helper}_char__({kind} out, {kind} str, __sea_type_char__ c)", "{",
            "\t__sea_type_nat__ i = 0;",
            "\tfor(; i < str.size; i++) "
            "((__sea_type_str__)out.data)[i] = ((__sea_type_str__)str.data)[i];",
            "\t((__sea_type_str__)out.data)[i++] = c;",
            "\t((__sea_type_str__)out.data)[i] = '\\0';",
            "\treturn out;", "}",
            f"{kind} {helper}_char_left__({kind} out, __sea_type_char__ c, {kind} str)", "{",
            "\t__sea_type_nat__ i = 0;",
            "\t((__sea_type_str__)out.data)[i++] = c;",
            "\tfor(i = 0; i < str.size; i++) "
            "((__sea_type_str__)out.data)[i + 1] = ((__sea_type_str__)str.data)[i];",
            "\t((__sea_type_str__)out.data)[i + 1] = '\\0';",
            "\treturn out;", "}",
            f"{kind} {helper}_str__({kind} out, {kind} str1, {kind} str2)", "{",
            "\t__sea_type_nat__ i = 0;",
            "\tfor(; i < str1.size; i++) "
            "((__sea_type_str__)out.data)[i] = ((__sea_type_str__)str1.data)[i];",
            "\tfor(i = 0; i < str2.size; i++) "
            "((__sea_type_str__)out.data)[str1.size + i] = ((__sea_type_str__)str2.data)[i];",
            "\t((__sea_type_str__)out.data)[str1.size + i] = '\\0';",
            "\treturn out;", "}",
            f"#define {helper}_order__(OUT, STR1, STR2) _Generic((STR1), \\",
            f"\t__sea_type_char__: {helper}_char_left__, \\",
            f"\tdefault: {helper}_str__)",
            f"#define {func}(OUT, STR1, STR2) _Generic((STR2), \\",
            f"\t__sea_type_char__: {helper}_char__, \\",
            f"\tdefault: {helper}_order__(OUT, STR1, STR2))(OUT, STR1, STR2)"
        ))

    def transpile_array(self, left, right):
        if left.arrays != right.arrays:
            l_title = f"{left.arrays}D array" if left.arrays > 0 else "non-array"
            r_title = f"{right.arrays}D array" if right.arrays > 0 else "non-array"
            self.transpiler.warnings.error(self, f"Cannot add {l_title} to {r_title}")

        if left.kind == "str" and right.kind != "str":
            self.transpiler.warnings.error(self, "Cannot add non-str array to str array")

        if left.kind != "str" and right.kind == "str":
            self.transpiler.warnings.error(self, "Cannot add str array to non-str array")

        result = Expression.resolve(left, right, True, True).cast_up()
        self.transpiler.temps.cache_new_array(result, f"{right}.size + {left}.size")

        o_kind = result.kind if result.kind != "str" and result.arrays < 2 else "array"
        l_kind = left.kind if left.kind != "str" and left.arrays < 2 else "array"
        r_kind = right.kind if right.kind != "str" and right.arrays < 2 else "array"

        append = util(self.util_array_append(o_kind, l_kind, r_kind))
        result.add(f"{append}(", f", {left}, {right})")
        return self.transpiler.temps.cache_new(result)

    @staticmethod
    def util_array_append(o_kind, l_kind, r_kind):
        name = f"array_append_{l_kind}_{r_kind}_into_{o_kind}"

        kind = "__sea_type_array__"
        o_kind = f"__sea_type_{o_kind}__"
        l_kind = f"__sea_type_{l_kind}__"
        r_kind = f"__sea_type_{r_kind}__"

        @new_util(name)
        def func(func):
            return "\n".join((
                f"{kind} {func}({kind} out, {kind} left, {kind} right)", "{",
                "\t__sea_type_nat__ i = 0;",
                "\tfor(; i < left.size; i++) "
                f"(({o_kind} *)out.data)[i] = (({l_kind} *)left.data)[i];",
                "\tfor(i = 0; i < right.size; i++) "
                f"(({o_kind} *)out.data)[left.size + i] = (({r_kind} *)right.data)[i];",
                "\treturn out;", "}"
            ))

        return name
