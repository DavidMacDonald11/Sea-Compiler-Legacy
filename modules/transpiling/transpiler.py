from .context import Context
from .symbol_table import SymbolTable
from .expression import Expression
from .statement import Statement
from .symbols.function import FunctionKind

class Transpiler:
    @property
    def temp_name(self):
        self.temps += 1
        return f"__sea_temp_value_{self.temps}__"

    def __init__(self, warnings, filepath):
        self.warnings = warnings
        self.file = open(filepath, "w", encoding = "UTF-8")
        self.context = Context()
        self.symbols = SymbolTable()
        self.includes = []
        self.wrote = []
        self.lines = ""
        self.temps = -1

        self.standard()

    def __del__(self):
        self.close()

    def close(self):
        if self.file.closed: return

        self.header("\n".join((
            "\n/* FILE CONTENTS */",
            f"{self.lines.strip()}",
            "/* FILE CONTENTS */\n",
            "int main(__sea_type_nat__ argc, __sea_type_str__ argv[])", "{",
            "\t__sea_type_array__ str_args[argc];\n",
            "\tfor(__sea_type_nat__ i = 0; i < argc; i++)", "\t{",
            "\t\tstr_args[i] = (__sea_type_array__){argv[i], strlen(argv[i])};", "\t}\n",
            "\treturn __sea_fun_main__((__sea_type_array__){str_args, argc});", "}"
        )))

        self.file.close()

    def standard(self):
        self.include("stdint")
        self.include("limits")
        self.include("string")
        self.header()

        for i in range(3, 7):
            bits = 2 ** i
            self.alias(f"int_least{bits}_t", f"__sea_type_int{bits}__")
            self.alias(f"uint_least{bits}_t", f"__sea_type_nat{bits}__")

        self.alias("__sea_type_nat8__", "__sea_type_bool__")
        self.alias("__sea_type_nat8__", "__sea_type_char__")
        self.alias("intmax_t", "__sea_type_int__")
        self.alias("uintmax_t", "__sea_type_nat__")

        self.alias("float", "__sea_type_real32__")
        self.alias("double", "__sea_type_real64__")
        self.alias("long double", "__sea_type_real__")
        self.alias("float", "__sea_type_imag32__")
        self.alias("double", "__sea_type_imag64__")
        self.alias("long double", "__sea_type_imag__")
        self.alias("_Complex float", "__sea_type_cplex32__")
        self.alias("_Complex double", "__sea_type_cplex64__")
        self.alias("_Complex long double", "__sea_type_cplex__")
        self.alias("__sea_type_char__*", "__sea_type_str__")

        self.header("\n".join((
            "typedef struct {",
            "\tvoid *data;", "\t__sea_type_nat__ size;",
            "} __sea_type_array__;",
            "__sea_type_array__ __sea_special_null_array__ = {0, 0};"
        )))

        self.header()

        r_type = FunctionKind(None, None, 0, None)
        null_array = Expression("", '__sea_special_null_array__')
        parameters = [
            FunctionKind("invar", "str", 0, None, ("string", null_array)),
            FunctionKind("invar", "str", 0, None, ("end", null_array))
            ]

        main = self.symbols.new_function(None, "main")
        main.return_type = FunctionKind(None, "int", 0, None)
        main.parameters = [FunctionKind("var", "str", 1, None)]
        main.declared = True

        self.standard_function(r_type, "print", parameters, "\n".join((
            "\nvoid __sea_fun_print__(__sea_type_array__ s, __sea_type_array__ end)", "{",
            '\tprintf("%s%s", (s.data) ? (char *)s.data : "", '
            '(end.data) ? (char *)end.data : "\\n");', "}"
        )), ["stdio"])

        r_type = FunctionKind("var", "nat", 0, None)
        parameters = [FunctionKind("invar", "any", 0, None)]

        self.standard_function(r_type, "len", parameters, "\n".join((
            "\n#define __sea_fun_len__(X) _Generic((X), __sea_type_array__: X, \\",
            "\tdefault: __sea_special_null_array__).size"
        )), [])

    def standard_function(self, r_type, name, parameters, definition, includes):
        def define():
            for include in includes:
                self.include(include)

            self.header(definition)

        self.symbols.new_standard_function(r_type, name, parameters, define)

    def include(self, header):
        if header not in self.includes:
            self.includes += [header]
            self.header(f"#include <{header}.h>")

    def header(self, string = "", end = "\n"):
        self.file.write(f"{string}{end}")

    def alias(self, c_name, sea_name):
        self.header(f"typedef {c_name} {sea_name};")

    def write(self, string = "", end = "\n"):
        self.lines += f"{string}{end}"

    def new_temp(self, statement, kind = None):
        kind = kind or (statement.expression.kind, 0)
        name =  self.temp_name

        prefix = Expression(kind[0], statement.expression.string, kind[1])
        prefix.add(f"__sea_type_{kind[0]}__ {'*' * kind[1]}{name} = ")

        return statement.prefix(prefix).new(name)

    def cache_new_temp(self, expression, name = None, string = False):
        name = name or self.temp_name
        kind = expression.kind

        prefix = Expression(kind, expression.string)
        kind = "array" if not string and kind == "str" or expression.arrays > 0 else kind
        prefix.add(f"__sea_type_{kind}__ {name} = ")
        Statement.cached += [prefix]

        return expression.new(name)

    def cache_new_temp_buffer(self, expression):
        prefix = Expression(expression.kind, expression.string)

        size = self.temp_name
        buffer = self.temp_name
        name = self.temp_name

        func = self.write_buffer_func()
        prefix.add(f"{func}({name}, {buffer}, {size}, ", ")")
        Statement.cached += [prefix]

        return expression.new(name)

    def cache_new_temp_str(self, expression):
        prefix = Expression(expression.kind, expression.string)
        buffer = self.temp_name
        name = self.temp_name

        func = self.write_str_array_func()
        prefix.add(f"{func}({buffer}, {name}, ", ")")
        Statement.cached += [prefix]

        return expression.new(name)

    def cache_new_temp_array(self, expression, size, string = False):
        prefix = Expression(expression.kind, expression.string)
        kind = expression.kind

        if not string and kind == "str" or expression.arrays > 1:
            kind = "array"
        elif self.context.array is not None:
            if self.context.array.kind != "str":
                prefix.cast(self.context.array.kind)
                expression.cast(self.context.array.kind)

            kind = "array" if expression.arrays > 1 else self.context.array.kind

        name = self.temp_name
        buffer = self.temp_name
        kind = f"__sea_type_{kind}__"

        if prefix.string != "":
            assign = True
            prefix.new(f", {prefix.string[1:-1]}")
        else:
            assign = False

        func = self.write_array_func(assign)
        prefix.add(f"{func}({name}, {kind}, {buffer}, {size}", ")")
        Statement.cached += [prefix]

        return expression.new(name)

    def push_symbol_table(self):
        self.symbols = SymbolTable(self.symbols)

    def pop_symbol_table(self):
        type(self.symbols).count -= 1
        self.symbols = self.symbols.parent

    def write_buffer_func(self):
        func = "__sea_func_buffer__"
        if func in self.wrote: return func
        self.wrote += [func]

        self.header("\n".join((
            f"#define {func}(ARRAY, BUFFER, SIZE, STR, THING) \\",
            "\t__sea_type_nat__ SIZE = snprintf(NULL, 0, STR, THING); \\",
            "\t__sea_type_char__ BUFFER[1 + SIZE]; \\",
            "\tsprintf(BUFFER, STR, THING); \\",
            "__sea_type_array__ ARRAY = {BUFFER, SIZE}"
        )))

        return func

    def write_str_array_func(self):
        func = "__sea_func_str_array__"
        if func in self.wrote: return func
        self.wrote += [func]

        self.header("\n".join((
            f"#define {func}(STR, ARRAY, LITERAL) \\",
            "\t__sea_type_str__ STR = LITERAL; \\",
            "\t__sea_type_array__ ARRAY = {STR, strlen(STR)}"
        )))

        return func

    def write_array_func(self, assign):
        func = f"__sea_func_array{'_assign' if assign else ''}__"
        if func in self.wrote: return func
        self.wrote += [func]

        self.header("\n".join((
            f"#define {func}(ARRAY, TYPE, BUFFER, SIZE{', ...' if assign else ''}) \\",
            f"\tTYPE BUFFER[SIZE]{' = {__VA_ARGS__}' if assign else ''};\\",
            "\t__sea_type_array__ ARRAY = {BUFFER, SIZE}",
        )))

        return func
