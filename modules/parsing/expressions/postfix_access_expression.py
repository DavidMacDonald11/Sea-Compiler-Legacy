from transpiling.expression import Expression, FLOATING_TYPES
from ..node import Node

class PostfixAccessExpression(Node):
    wrote = []

    @property
    def nodes(self) -> list:
        nodes = [self.expression]
        nodes += [split for split in self.splits if split is not None]
        return nodes

    def __init__(self, splits):
        self.splits = splits
        self.expression = None

    @classmethod
    def construct(cls):
        count = 0
        splits = []
        found = None

        while not cls.parser.next.has("]", r"\n", "EOF"):
            while cls.parser.next.has(":"):
                last = cls.parser.take()
                splits += [found]
                count += 1
                found = None

            if cls.parser.next.has("]", r"\n", "EOF"):
                break

            if found is not None: count += 1
            last = found = cls.parser.expression.construct()

        token = cls.parser.expecting_has("]")
        splits += [found]

        if len(splits) > 3:
            cls.parser.warnings.error(last, "Too many split arguments")

        if count >= len(splits):
            cls.parser.warnings.error(last, "Split arguments must be separated by ':'")

        if len(splits) == 1 and splits[0] is None:
            cls.parser.warnings.error(token, "Cannot have empty access expression")

        return cls(splits)

    def transpile(self):
        expression = self.expression.transpile()

        if expression.kind != "str" and expression.arrays == 0:
            self.transpiler.warnings.error(self.expression, "Cannot access non-array")

        if len(self.splits) > 1:
            return self.transpile_split(expression)

        index = self.verify_arg(self.splits[0].transpile())

        if expression.kind == "str" and expression.arrays == 0:
            func = self.write_str_index_func()
            return expression.add(f"{func}(", f", {index})").cast("char")

        func = self.write_array_index_func()
        expression.arrays -= 1

        kind = "array" if expression.kind == "str" else expression.kind
        return expression.add(f"{func}(__sea_type_{kind}__, ", f", {index})")

    def transpile_split(self, expression):
        expression, start, stop, step = self.transpile_args(expression)
        size_func = self.write_split_size_func()
        size = Expression("nat", f"{size_func}({start}, {stop}, {step})")
        size = self.transpiler.cache_new_temp(size)

        result = self.transpiler.cache_new_temp_array(expression.copy().new(""), size)

        if expression.kind == "str" and expression.arrays == 0:
            func = self.write_str_split_func()
            return expression.add(f"{func}({result}, ", f", {start}, {stop}, {step})")

        kind = "array" if expression.kind == "str" else expression.kind
        func = self.write_array_split_func(kind)
        return expression.add(f"{func}({result}, ", f", {start}, {stop}, {step})")

    def transpile_args(self, expression):
        array = self.transpiler.cache_new_temp(expression)

        if len(self.splits) < 3 or self.splits[2] is None:
            step = Expression("nat8", "1")
        else:
            step = self.verify_arg(self.splits[2].transpile())

        if len(self.splits) < 2 or self.splits[1] is None:
            stop = Expression("nat", f"(({step} < 0) ? {array}.size - 1: {array}.size)")
        else:
            stop = self.verify_arg(self.splits[1].transpile())

        if self.splits[0] is None:
            start = Expression("nat8", f"(({step} < 0) ? -1 : 0)")
        else:
            start = self.verify_arg(self.splits[0].transpile())

        return array, start, stop, step

    def verify_arg(self, arg):
        arg.operate(self)

        if arg.kind in FLOATING_TYPES:
            self.transpiler.warnings.error(self, "Cannot use floating type as access argument")

        return arg

    def write_array_index_func(self):
        func = "__sea_func_array_index__"
        if func in type(self).wrote: return func
        type(self).wrote += [func]

        helper = "__sea_func_array_safe_i"

        self.transpiler.header("\n".join((
            f"__sea_type_nat__ {helper}_nat__(__sea_type_nat__ i, __sea_type_nat__ size)", "{",
            "\twhile(i >= size) i -= size;", "\treturn i;", "}",
            f"\n__sea_type_nat__ {helper}_int__(__sea_type_int__ i, __sea_type_nat__ size)", "{",
            "\twhile(i < 0) i += size;", f"\treturn {helper}_nat__(i, size);", "}",
            f"\n#define {helper}__(arr, i) _Generic((i), __sea_type_nat__: {helper}_nat__, \\",
            f"\tdefault: {helper}_int__)(i, arr.size)",
            f"\n#define {func}(type, name, i) (((type *)name.data)[{helper}__(name, i)])"
        )))

        return func

    def write_str_index_func(self):
        func = "__sea_func_str_index__"
        if func in type(self).wrote: return func
        type(self).wrote += [func]

        helper = "__sea_func_str_safe_i"

        self.transpiler.header("\n".join((
            f"__sea_type_nat__ {helper}_nat__(__sea_type_nat__ i, __sea_type_nat__ size)", "{",
            "\treturn (i > size) ? size : i;", "}",
            f"__sea_type_nat__ {helper}_int__(__sea_type_int__ i, __sea_type_nat__ size)", "{",
            "\tif(i < 0) i += size;", f"\treturn {helper}_nat__((i < 0) ? size : i, size);", "}",
            f"\n#define {helper}__(str, i) _Generic((i), __sea_type_nat__: {helper}_nat__, \\",
            f"\tdefault: {helper}_int__)(i, str.size)",
            f"\n#define {func}(name, i) (((__sea_type_str__)name.data)[{helper}__(name, i)])"
        )))

        return func

    def write_split_size_func(self):
        func = "__sea_func_split_size__"
        if func in type(self).wrote: return func
        type(self).wrote += [func]

        kind = "__sea_type_int__"

        self.transpiler.header("\n".join((
            f"__sea_type_nat__ {func}({kind} start, {kind} stop, {kind} step)", "{",
            "\tif(step == 0) return 1;", "",
            "\t__sea_type_nat__ count = 0;", "",
            "\tdo {",
            "\t\tcount += 1;",
            "\t\tif(step < 0) stop += step;",
            "\t\telse start += step;",
            "\t} while(start < stop);", "",
            "\treturn count;", "}"
        )))

        return func

    def write_array_split_func(self, kind):
        func = f"__sea_func_split_array_{kind}__"
        if func in type(self).wrote: return func
        type(self).wrote += [func]

        index = self.write_array_index_func()

        kind = f"__sea_type_{kind}__"
        arr_kind = "__sea_type_array__"
        int_kind = "__sea_type_int__"

        numbers = f"{int_kind} start, {int_kind} stop, {int_kind} step"

        self.transpiler.header("\n".join((
            f"{arr_kind} {func}({arr_kind} out, {arr_kind} in, {numbers})", "{",
            "\tif(step < 0) start = stop;",
            "\tfor(__sea_type_nat__ i = 0; i < out.size; i++) {",
            f"\t\t{index}({kind}, out, i) = {index}({kind}, in, start);",
            "\t\tstart += step;", "\t}",
            "\treturn out;", "}"
        )))

        return f"{func}"

    def write_str_split_func(self):
        func = "__sea_func_split_str__"
        if func in type(self).wrote: return func
        type(self).wrote += [func]

        index = self.write_str_index_func()

        arr_kind = "__sea_type_array__"
        int_kind = "__sea_type_int__"

        numbers = f"{int_kind} start, {int_kind} stop, {int_kind} step"

        self.transpiler.header("\n".join((
            f"{arr_kind} {func}({arr_kind} out, {arr_kind} in, {numbers})", "{",
            "\tif(step < 0) start = stop;",
            "\tfor(__sea_type_nat__ i = 0; i < out.size; i++) {",
            f"\t\t{index}(out, i) = {index}(in, start);",
            "\t\tstart += step;", "\t}",
            "\treturn out;", "}"
        )))

        return func
