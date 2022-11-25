from .context import Context
from .symbol_table import SymbolTable
from .expression import Expression

class Transpiler:
    @property
    def expression(self):
        return Expression

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

        self.include("complex")
        self.include("stdio")

        self.file.write("\n".join((
            "\nvoid __sea_fun_cprint__(__sea_type_cmax__ c)", "{",
            '\tprintf("%Lf + %Lfi\\n", creall(c), cimagl(c));', "}",
            f"{self.lines}int main() {{ return __sea_fun_main__(); }}\n"
        )))

        self.file.close()

    def standard(self):
        self.include("stdint")
        self.include("limits")
        self.header()

        self.alias("float", "__sea_type_f32__")
        self.alias("double", "__sea_type_f64__")
        self.alias("long double", "__sea_type_fmax__")
        self.alias("double", "__sea_type_g64__")
        self.alias("long double", "__sea_type_gmax__")
        self.alias("_Complex float", "__sea_type_c32__")
        self.alias("_Complex double", "__sea_type_c64__")
        self.alias("_Complex long double", "__sea_type_cmax__")

        for i in range(3, 7):
            bits = 2 ** i
            self.alias(f"int_least{bits}_t", f"__sea_type_i{bits}__")
            self.alias(f"uint_least{bits}_t", f"__sea_type_u{bits}__")

        self.alias("intmax_t", "__sea_type_imax__")
        self.alias("uintmax_t", "__sea_type_umax__")

        self.header()

        cprint = self.symbols.new_function(None, "void", "cprint")
        cprint.parameters = [("invar", "cplex", None)]
        cprint.declared = cprint.defined = True

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

    def new_temp(self, expression):
        expression = expression.copy().cast_up()

        c_type = expression.c_type
        c_name = f"__sea_temp_value_{self.temps}__"
        self.temps += 1

        return expression.copy().new(f"{c_type} {c_name} = %s;"), expression.new(c_name)

    def push_symbol_table(self):
        self.symbols = SymbolTable(self.symbols)

    def pop_symbol_table(self):
        type(self.symbols).count -= 1
        self.symbols = self.symbols.parent
