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
    @property
    def c_name(self):
        return f"__sea_var_{self.name}__"
