class SymbolTable:
    count = 0

    def __init__(self, parent = None):
        type(self).count += 1

        self.symbols = {}
        self.parent = parent
        self.number = type(self).count

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

    def new_variable(self, node, s_type, name):
        return self._new_identifier(Variable, node, s_type, name)

    def new_invariable(self, node, s_type, name):
        return self._new_identifier(Invariable, node, s_type, name)

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
