from parsing.declarations.type_keyword import TYPE_MAP
from .symbol_table import SymbolTable

class Transpiler:
    def __init__(self, warnings, filepath):
        self.warnings = warnings
        self.file = open(filepath, "w", encoding = "UTF-8")
        self.symbols = SymbolTable()
        self.includes = []
        self.lines = ""

        self.standard()

    def __del__(self):
        self.close()

    def close(self):
        if self.file.closed: return

        self.file.write("\n".join((
            "#include <stdio.h>",
            "int main()", "{",
            f"{self.lines}",
            'printf("Success!\\n");',
            "return 0;", "}"
        )))

        self.file.close()

    def standard(self):
        self.include("stdint")
        self.include("limits")
        self.header()

        self.alias("float", "__sea_type_f32__")
        self.alias("double", "__sea_type_f64__")
        self.alias("long double", "__sea_type_fmax__")
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

    def resolve_type(self, e_type1, e_type2):
        if e_type1 == e_type2 == "bool": return "u64"
        return e_type1 if POINTS[e_type1] > POINTS[e_type2] else e_type2

    def safe_type(self, e_type):
        return f"__sea_type_{e_type}__"

    def c_type(self, s_type):
        return TYPE_MAP[s_type]

POINTS = {
    "bool": 0,
    "u64": 1,
    "i64": 2,
    "umax": 2.25,
    "imax": 2.5,
    "f64": 3,
    "fmax": 3.5,
    "c64": 4,
    "cmax": 4.5
}
