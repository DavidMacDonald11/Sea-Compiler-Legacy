from .expression import Expression, OwnershipExpression
from .statement import Statement
from .utils import util, new_util

class Temps:
    def __init__(self, context):
        self.i = -1
        self.context = context

    def new_name(self):
        self.i += 1
        return f"__sea_temp_{self.i}__"

    def save(self, statement, prefix, cache):
        if cache:
            Statement.cached += [prefix]
        else:
            statement.prefix(prefix)

    def new(self, statement, string = False, cache = False):
        name = self.new_name()
        expression = statement if cache else statement.expression

        prefix = Expression(expression.kind, expression.string)
        ptr = "*" if isinstance(expression, OwnershipExpression) else ""

        kind = prefix.kind
        kind = "array" if not string and kind == "str" or expression.arrays > 0 else kind
        prefix.add(f"__sea_type_{kind}__ {ptr}{name} = ")

        self.save(statement, prefix, cache)
        return statement.new(name)

    def new_heap(self, statement, cache = False):
        name = self.new_name()
        expression = statement if cache else statement.expression

        prefix = Expression(expression.kind, expression.string)
        kind = f"__sea_type_{prefix.kind}__"
        alloc = util("alloc")

        e_kind = expression.kind
        e_arrays = expression.arrays

        if e_kind == "str" or e_arrays > 0:
            array = self.new_name()
            kind = "__sea_type_array__"
            alloc_array = util("alloc_array")

            size = f"sizeof(__sea_type_{'char' if e_kind == 'str' else e_kind}__)"
            string = int(e_kind == "str")
            prefix.add(f"{kind} {array} = {alloc_array}(", f", {e_arrays}, {string}, {size})")
            self.save(statement, prefix, cache)

            prefix = Expression(expression.kind)
            expression.new(f"&{array}")

        prefix.new(f"{kind} *{name} = {alloc}(1, sizeof({kind}))")
        self.save(statement, prefix, cache)

        prefix = OwnershipExpression(None, "$", expression.kind, expression.string)
        prefix.add(f"memcpy({name}, ", f", sizeof({kind}))")

        self.save(statement, prefix, cache)
        return statement.new(name)

    def new_str(self, statement, casted = False, cache = False):
        expression = statement if cache else statement.expression
        prefix = Expression(expression.kind, expression.string)
        buffer = self.new_name()
        name = self.new_name()

        if not casted:
            func = util("new_str")
            prefix.add(f"{func}({name}, {buffer}, ", ")")
        else:
            size = self.new_name()
            func = util("new_casted_str")
            prefix.add(f"{func}({name}, {buffer}, {size}, ", ")")

        self.save(statement, prefix, cache)
        return statement.new(name)

    def new_array(self, statement, size, string = False, cache = False):
        expression = statement if cache else statement.expression
        prefix = Expression(expression.kind, expression.string)
        kind = expression.kind

        if not string and kind == "str" or expression.arrays > 1:
            kind = "array"

        if self.context.array is not None:
            if self.context.array.kind != "str":
                prefix.cast(self.context.array.kind)
                expression.cast(self.context.array.kind)

            kind = "array" if expression.arrays > 1 else self.context.array.kind

        name = self.new_name()
        buffer = self.new_name()
        kind = f"__sea_type_{kind}__"

        if prefix.string != "":
            assign = True
            prefix.new(f", {prefix.string[1:-1]}")
        else:
            assign = False

        func = util(self.util_new_array(assign))
        prefix.add(f"{func}({name}, {kind}, {buffer}, {size}", ")")

        self.save(statement, prefix, cache)
        return statement.new(name)

    def copy_str(self, statement, cache = False):
        expression = statement if cache else statement.expression
        buffer = self.new_name()
        name, string = expression.string.split(" = ")

        parts = name.split(" ")

        if len(parts) > 1:
            prefix = Expression(expression.kind, name)
            self.save(statement, prefix, cache)
            name = parts[1]

        func = util("copy_str")
        return statement.new(f"{func}({name}, {string}, {buffer})")

    @new_util("alloc")
    @staticmethod
    def util_alloc(func):
        return "\n".join((
            f"void *{func}(size_t nitems, size_t size)", "{",
            "\tvoid *p = calloc(nitems, size);",
            "\tif(!p) exit(14);",
            "\treturn p;", "}"
        ))

    @new_util("alloc_array")
    @staticmethod
    def util_alloc_array(func):
        kind = "__sea_type_array__"
        nat = "__sea_type_nat__"
        alloc = util("alloc")

        return "\n".join((
            f"{kind} {func}({kind} *arr, {nat} dim, {nat} s, size_t size)", "{",
            "\tvoid *data;", "",
            "\tif(dim + s == 1)", "\t{",
            f"\t\tdata = {alloc}(arr->size + s, size);",
            "\t\tmemcpy(data, arr->data, (arr->size + s) * size);", "\t}",
            "\telse", "\t{",
            f"\t\tdata = {alloc}(arr->size, sizeof({kind}));", "",
            f"\t\tfor({nat} i = 0; i < arr->size; i++)", "\t\t{",
            f"\t\t\t{kind} *elem = &(({kind} *)arr->data)[i];",
            f"\t\t\t{kind} new_elem = {func}(elem, dim - 1, s, size);",
            f"\t\t\tmemcpy(({kind} *)data + i, &new_elem, sizeof({kind}));", "\t\t}", "\t}", "",
            f"\treturn ({kind}){{data, arr->size}};", "}"
        ))

    @new_util("new_casted_str")
    @staticmethod
    def util_new_casted_str(func):
        return "\n".join((
            f"#define {func}(ARRAY, BUFFER, SIZE, STR, THING) \\",
            "\t__sea_type_nat__ SIZE = snprintf(NULL, 0, STR, THING); \\",
            "\t__sea_type_char__ BUFFER[1 + SIZE]; \\",
            "\tsprintf(BUFFER, STR, THING); \\",
            "\t__sea_type_array__ ARRAY = {BUFFER, SIZE}"
        ))

    @new_util("new_str")
    @staticmethod
    def util_new_str(func):
        return "\n".join((
            f"#define {func}(ARRAY, STR, LITERAL) \\",
            "\t__sea_type_str__ STR = LITERAL; \\",
            "\t__sea_type_array__ ARRAY = {STR, strlen(STR)}"
        ))

    @staticmethod
    def util_new_array(assign):
        name = f"new_array{'_assign' if assign else ''}"

        @new_util(name)
        def func(func):
            return "\n".join((
                f"#define {func}(ARRAY, TYPE, BUFFER, SIZE{', ...' if assign else ''}) \\",
                f"\tTYPE BUFFER[SIZE]{' = {__VA_ARGS__}' if assign else ''}; \\",
                "\t__sea_type_array__ ARRAY = {BUFFER, SIZE}",
            ))

        return name

    @new_util("copy_str")
    @staticmethod
    def util_copy_str(func):
        return "\n".join((
            f"#define {func}(OUT, IN, BUFFER) \\",
            "\t__sea_type_char__ BUFFER[IN.size + 1]; \\",
            "\tOUT = (__sea_type_array__){BUFFER, IN.size}; \\",
            "\tmemcpy(BUFFER, IN.data, IN.size + 1)"
        ))

# TODO create a copy of array on assign
# TODO stack array of heap str doesn't work
# TODO all large arrays/str should be on heap
# TODO check if heap for + and *
# TODO conditional ownership prevents freeing of memory
