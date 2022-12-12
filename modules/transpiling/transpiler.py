from .context import Context
from .symbol_table import SymbolTable
from .expression import Expression
from .symbols.function import FunctionKind
from .temps import Temps
from .utils import set_transpiler

class Transpiler:
    @property
    def temp_name(self):
        return "__sea_temp_value_69__"

    def __init__(self, warnings, filepath):
        self.warnings = warnings
        self.file = open(filepath, "w", encoding = "UTF-8")
        self.context = Context()
        self.symbols = SymbolTable()
        self.temps = Temps(self.context)
        self.includes = []
        self.head = ""
        self.lines = ""

        set_transpiler(self)
        self.standard()

    def __del__(self):
        self.close()

    def close(self):
        if self.file.closed: return

        self.file.write("\n".join((
            f"\n{self.head.strip()}\n",
            "/* FILE CONTENTS */",
            f"{self.lines.strip()}",
            "/* FILE CONTENTS */\n",
            "int main(__sea_type_nat__ argc, __sea_type_str__ argv[])", "{",
            "\t__sea_type_array__ str_args[argc];\n",
            "\tfor(__sea_type_nat__ i = 0; i < argc; i++)", "\t{",
            "\t\tstr_args[i] = (__sea_type_array__){argv[i], strlen(argv[i])};", "\t}\n",
            "\treturn __sea_fun_main__((__sea_type_array__){str_args, argc});", "}\n"
        )))

        self.file.close()

    def standard(self):
        self.include("stdint")
        self.include("limits")
        self.include("string")

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
            "\ntypedef struct {",
            "\tvoid *data;", "\t__sea_type_nat__ size;",
            "} __sea_type_array__;\n",
            "__sea_type_array__ __sea_special_null_array__ = {0, 0};"
        )))


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
            "void __sea_fun_print__(__sea_type_array__ s, __sea_type_array__ end)", "{",
            '\tprintf("%s%s", (s.data) ? (char *)s.data : "", '
            '(end.data) ? (char *)end.data : "\\n");', "}"
        )), ["stdio"])

        r_type = FunctionKind("var", "nat", 0, None)
        parameters = [FunctionKind("invar", "any", 0, None)]

        self.standard_function(r_type, "len", parameters, "\n".join((
            "#define __sea_fun_len__(X) _Generic((X), __sea_type_array__: X, \\",
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
            self.file.write(f"#include <{header}.h>\n")

    def header(self, string = "", end = "\n\n"):
        self.head += f"{string}{end}"

    def alias(self, c_name, sea_name):
        self.header(f"typedef {c_name} {sea_name};", "\n")

    def write(self, string = "", end = "\n"):
        self.lines += f"{string}{end}"

    def push_symbol_table(self):
        self.symbols = SymbolTable(self.symbols)

    def pop_symbol_table(self):
        type(self.symbols).count -= 1
        self.symbols = self.symbols.parent
