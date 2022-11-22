class SymbolTable:
    count = 0

    def __init__(self, parent = None):
        type(self).count += 1

        self.symbols = {}
        self.parent = parent
        self.number = type(self).count

    def __repr__(self):
        if self.parent is None:
            return f"{self.number} {self.symbols}"

        return f"{self.parent},\n    {self.number} {self.symbols}"

    def at(self, node, key):
        if key in self.symbols:
            return self.symbols[key]

        if self.parent is not None:
            return self.parent.at(node, key)

        node.transpiler.warnings.error(node, f"Reference to undeclared identifier '{key}'")
        return None

    def _new_identifier(self, cls, node, s_type, name):
        if name in self.symbols:
            message = f"Cannot declare identifier '{name}' twice."
            node.transpiler.warnings.error(node, message)
            return None

        self.symbols[name] = identifier = cls(s_type, name, self.number)
        return identifier

    def new_label(self, node, name):
        return self._new_identifier(Label, node, None, name)

    def new_variable(self, node, s_type, name):
        return self._new_identifier(Variable, node, s_type, name)

    def new_invariable(self, node, s_type, name):
        return self._new_identifier(Invariable, node, s_type, name)

    def new_function(self, node, s_type, name):
        return self._new_identifier(Function, node, s_type, name)

class Identifier:
    @property
    def c_name(self):
        raise NotImplementedError(type(self).__name__)

    def __init__(self, s_type, name, table_number):
        self.s_type = s_type
        self.name = name
        self.table_number = table_number

    def __repr__(self):
        return self.c_name

class Label(Identifier):
    @property
    def c_name(self):
        return f"__sea_label_{self.name}"

    def surround(self, expression):
        return expression.new(f"{self.c_name}_continue__: %s {self.c_name}_break__:")

class Variable(Identifier):
    @property
    def c_name(self):
        return f"__sea_var_{self.name}__"

    @property
    def c_access(self):
        return f"(*{self.c_name})" if self.ownership is not None else self.c_name

    def __init__(self, s_type, name, table_number):
        self.initialized = False
        self.is_transfered = False
        self.ownership = None
        super().__init__(s_type, name, table_number)

    def access(self, node, expression):
        if self.is_transfered:
            node.transpiler.warnings.error(node, "Cannot use dead identifier after ownership swap")

        expression = expression.new(self.c_access).cast(self.s_type)
        expression.is_invar = isinstance(self, Invariable)

        if self.initialized:
            return expression

        node.transpiler.warnings.error(node, f"Accessing uninitialized identifier '{self.name}'")
        return expression.new("/*%s*/")

    def assign(self, node, expression):
        if self.is_transfered:
            node.transpiler.warnings.error(node, "Cannot use dead identifier after ownership swap")

        if not self.initialized:
            self.initialized = True
            self.ownership = expression.ownership

        if self.s_type == "bool" and expression.e_type not in "bool":
            node.transpiler.warnings.error(node, "".join((
                "Cannot assign non-bool value to bool identifier. ",
                "(Consider using the '?' operator to get boolean value)"
            )))

        if self.s_type not in ("imag32", "imag64", "imag"):
            return expression

        suffix = "f" if self.s_type == "imag32" else ("l" if self.s_type == "imag" else "")
        node.transpiler.include("complex")

        return expression.new(f"cimag{suffix}(%s)")

class Invariable(Variable):
    @property
    def c_name(self):
        return f"__sea_invar_{self.name}__"

    def assign(self, node, expression):
        if self.initialized:
            node.transpiler.warnings.error(node, f"Cannot reassign invariable '{self.name}'")

        return super().assign(node, expression)

class Function(Identifier):
    @property
    def c_name(self):
        return f"__sea_fun_{self.name}__"

    def __init__(self, s_type, name, table_number):
        self.parameters = None
        super().__init__(s_type, name, table_number)
