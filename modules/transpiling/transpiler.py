from .context import Context
from .symbol_table import SymbolTable
from .expression import Expression

class Transpiler:
    def __init__(self, warnings, filepath):
        self.warnings = warnings
        self.file = open(filepath, "w", encoding = "UTF-8")
        self.context = Context()
        self.symbols = SymbolTable()
        self.includes = []
        self.lines = ""
        self.temps = 0

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

        self.alias("float", "__sea_type_real32__")
        self.alias("double", "__sea_type_real64__")
        self.alias("long double", "__sea_type_real__")
        self.alias("float", "__sea_type_imag32__")
        self.alias("double", "__sea_type_imag64__")
        self.alias("long double", "__sea_type_imag__")
        self.alias("_Complex float", "__sea_type_cplex32__")
        self.alias("_Complex double", "__sea_type_cplex64__")
        self.alias("_Complex long double", "__sea_type_cplex__")

        for i in range(3, 7):
            bits = 2 ** i
            self.alias(f"int_least{bits}_t", f"__sea_type_int{bits}__")
            self.alias(f"uint_least{bits}_t", f"__sea_type_nat{bits}__")

        self.alias("intmax_t", "__sea_type_int__")
        self.alias("uintmax_t", "__sea_type_nat__")
        self.alias("__sea_type_nat8__", "__sea_type_char__")
        self.alias("__sea_type_nat8__", "__sea_type_bool__")
        self.alias("__sea_type_char__*", "__sea_type_str__")

        self.header()

        self.standard_function(None, "cprint", [("invar", "cplex", None)], "\n".join((
            "\nvoid __sea_fun_cprint__(__sea_type_cplex__ c)", "{",
            '\tprintf("%Lf + %Lfi\\n", creall(c), cimagl(c));', "}"
        )), ["complex", "stdio"])

        self.standard_function(None, "print", [("invar", "str", None)], "\n".join((
            "\nvoid __sea_fun_print__(__sea_type_str__ s)", "{",
            '\tprintf("%s", s);', "}"
        )), ["stdio"])

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

    def new_temp(self, statement):
        kind = statement.expression.kind
        name =  f"__sea_temp_value_{self.temps}__"
        self.temps += 1

        prefix = Expression(kind, statement.expression.string)
        prefix.add(f"__sea_type_{kind}__ {name} = ")

        return statement.prefix(prefix).new(name)

    def push_symbol_table(self):
        self.symbols = SymbolTable(self.symbols)

    def pop_symbol_table(self):
        type(self.symbols).count -= 1
        self.symbols = self.symbols.parent
