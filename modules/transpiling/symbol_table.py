class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def __getitem__(self, key):
        return self.symbols[key] if key in self.symbols else None

    def new_variable(self, s_type, name):
        if name in self.symbols:
            return None

        self.symbols[name] = var = Variable(s_type, name)
        return var.c_name

class Symbol:
    @property
    def c_name(self):
        raise NotImplementedError(f"{type(self).__name__} has no c_name property")

    def __init__(self, s_type, name):
        self.s_type = s_type
        self.name = name

class Variable(Symbol):
    def __init__(self, s_type, name):
        self.initialized = False
        super().__init__(s_type, name)

    @property
    def c_name(self):
        return f"__sea_var_{self.name}__"

    def access(self, node):
        if self.initialized: return self.c_name

        node.transpiler.warnings.error(node, f"Accessing uninitialized variable '{self.name}'")
        return f"/*{self.c_name}*/"

    def assign(self, node, e_type, expression, identifier = None):
        self.initialized = True
        identifier = identifier or self.c_name

        if self.s_type == "bool" and e_type != "bool":
            node.transpiler.warnings.error(node, "Cannot assign non-boolean value to bool variable")

        if self.s_type not in ("imag32", "imag64", "imag"):
            return (e_type, f"{identifier} = {expression}")

        suffix = "f" if self.s_type == "imag32" else ("l" if self.s_type == "imag" else "")
        node.transpiler.include("complex")
        return (e_type, f"{identifier} = cimag{suffix}({expression})")
