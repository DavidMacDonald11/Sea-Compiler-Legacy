class Transpiler:
    def __init__(self, warnings, filepath):
        self.warnings = warnings
        self.file = open(filepath, "w", encoding = "UTF-8")
        self.expression_type = None
        self.includes = []

        self.standard()

    def __del__(self):
        self.file.close()

    def standard(self):
        self.include("stdint")
        self.include("limits")
        self.write()

        self.alias("float", "f32")
        self.alias("double", "f64")

        for i in range(3, 7):
            bits = 2 ** i
            self.alias(f"int{bits}_t", f"i{bits}")
            self.alias(f"uint{bits}_t", f"u{bits}")

        self.write()

    def include(self, header):
        if header not in self.includes:
            self.includes += [header]
            self.write(f"#include <{header}.h>")

    def write(self, string = "", end = "\n"):
        self.file.write(f"{string}{end}")

    def alias(self, c_name, sea_name):
        self.write(f"typedef {c_name} {sea_name};")

    def set_type(self, e_type1, e_type2):
        points = {"u64": 1, "i64": 2, "f64": 3}
        self.expression_type = e_type1 if points[e_type1] > points[e_type2] else e_type2
