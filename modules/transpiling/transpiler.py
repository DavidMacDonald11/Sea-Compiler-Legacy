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
            "int main() { return __sea_fun_main__(); }"
        )))

        self.file.close()

    def standard(self):
        self.include("stdint")
        self.include("limits")
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

        r_type = FunctionKind(None, None, None)
        null_array = Expression("", '__sea_special_null_array__')
        parameters = [
            FunctionKind("invar", "str", None),
            FunctionKind("invar", "str", None, ("end", null_array))
            ]

        self.standard_function(r_type, "print", parameters, "\n".join((
            "\nvoid __sea_fun_print__(__sea_type_array__ s, __sea_type_array__ end)", "{",
            '\tprintf("%s%s", (char *)s.data, (end.data) ? (char *)end.data : "\\n");', "}"
        )), ["stdio"])

        r_type = FunctionKind("var", "nat", None)
        parameters = [FunctionKind("invar", "any", None)]

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

    def cache_new_temp(self, expression):
        name = self.temp_name
        prefix = Expression(expression.kind, expression.string)
        prefix.add(f"__sea_type_{expression.kind}__ {name} = ")
        Statement.cached += [prefix]

        return expression.new(name)

    def cache_new_temp_buffer(self, expression):
        prefix = Expression(expression.kind, expression.string)

        size_name = self.temp_name
        prefix.add(f"__sea_type_nat__ {size_name} = snprintf(NULL, 0, ", ")").cast("nat")
        Statement.cached += [prefix]

        buffer_name = self.temp_name
        prefix = Expression("str", size_name)
        prefix.add(f"__sea_type_char__ {buffer_name}[1 + ", "]")
        Statement.cached += [prefix]

        prefix = Expression("", expression.string)
        prefix.add(f"sprintf({buffer_name}, ", ")")
        Statement.cached += [prefix]

        name = self.temp_name
        prefix = Expression(expression.kind, size_name)
        prefix.add(f"__sea_type_array__ {name} = {{{buffer_name}, ", "}")
        Statement.cached += [prefix]

        return expression.new(name)

    def cache_new_temp_array(self, expression, size):
        prefix = Expression(expression.kind, expression.string)
        buffer_name = self.temp_name
        kind = expression.kind

        if size < 0:
            prefix.add(f"__sea_type_{kind}__ {buffer_name} = ")
            size = f"strlen({buffer_name})"
        else:
            if kind == "str" or expression.arrays > 1:
                kind = "array"
            elif self.context.array is not None:
                if self.context.array.kind != "str":
                    prefix.cast(self.context.array.kind)

                kind = "array" if expression.arrays > 1 else self.context.array.kind

            prefix.add(f"__sea_type_{kind}__ {buffer_name}[{size}] = ")

        Statement.cached += [prefix]

        name = self.temp_name
        prefix = Expression(expression.kind, buffer_name)
        prefix.add(f"__sea_type_array__ {name} = {{", f", {size}}}")
        Statement.cached += [prefix]

        return expression.new(name)

    def push_symbol_table(self):
        self.symbols = SymbolTable(self.symbols)

    def pop_symbol_table(self):
        type(self.symbols).count -= 1
        self.symbols = self.symbols.parent
