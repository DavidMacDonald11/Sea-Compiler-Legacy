class Transpiler:
    def __init__(self, warnings, filepath):
        self.warnings = warnings
        self.file = open(filepath, "w", encoding = "UTF-8")
        self.includes = []
        self.used = []

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

    def write(self, string = ""):
        self.file.write(f"{string}\n")

    def alias(self, c_name, sea_name):
        self.write(f"typedef {c_name} {sea_name};")

    def use(self, alias, bits):
        if alias not in self.used:
            self.used += [alias]
            message = f'"{alias} is not supported on this architecture"'
            self.write(f'_Static_assert(sizeof({alias}) * CHAR_BIT == {bits}, {message});')
