from .expression import Expression

class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def at(self, node, key):
        if key not in self.symbols:
            node.transpiler.warnings.error(node, f"Reference to undeclared identifier '{key}'")
            return None

        return self.symbols[key]

    def _new_identifier(self, cls, node, s_type, name, is_ref):
        if name in self.symbols:
            message = f"Cannot declare identifier '{name}' twice."
            node.tranpsiler.warnings.error(node, message)
            return None

        self.symbols[name] = identifier = cls(s_type, name, is_ref)
        return identifier

    def new_variable(self, node, s_type, name, is_ref = False):
        return self._new_identifier(Variable, node, s_type, name, is_ref)

    def new_invariable(self, node, s_type, name, is_ref = False):
        return self._new_identifier(Invariable, node, s_type, name, is_ref)

class Identifier:
    @property
    def c_name(self):
        raise NotImplementedError(type(self).__name__)

    def __init__(self, s_type, name):
        self.s_type = s_type
        self.name = name

    def __repr__(self):
        return self.c_name

class Variable(Identifier):
    @property
    def c_name(self):
        return f"__sea_var_{self.name}__"

    @property
    def declaration(self):
        return f"*{self.c_name}" if self.is_ref else self.c_name

    def __init__(self, s_type, name, is_ref):
        self.initialized = False
        self.is_transfered = False
        self.is_ref = is_ref
        super().__init__(s_type, name)

    def access(self, node):
        c_name = f"(*{self.c_name})" if self.is_ref else self.c_name

        if self.is_transfered:
            node.transpiler.warnings.error(node, "Cannot use dead identifier after ownership swap")

        if self.initialized: return c_name

        node.transpiler.warnings.error(node, f"Accessing uninitialized identifier '{self.name}'")
        return f"/*{c_name}*/"

    def assign(self, node, expression):
        if self.is_transfered:
            node.transpiler.warnings.error(node, "Cannot use dead identifier after ownership swap")

        ownership = expression.ownership
        is_invar = expression.is_invar

        self.initialized = True
        self.is_ref = ownership is not None

        if self.s_type == "bool" and expression.e_type not in "bool":
            node.transpiler.warnings.error(node, "".join((
                "Cannot assign non-bool value to bool identifier. ",
                "(Consider using the '?' operator to get boolean value)"
            )))

        if self.s_type not in ("imag32", "imag64", "imag"):
            return Expression(expression.e_type, f"{expression}", ownership, is_invar)

        suffix = "f" if self.s_type == "imag32" else ("l" if self.s_type == "imag" else "")
        node.transpiler.include("complex")

        return Expression(expression.e_type, f"cimag{suffix}({expression})", ownership, is_invar)

class Invariable(Variable):
    @property
    def c_name(self):
        return f"__sea_invar_{self.name}__"

    def assign(self, node, expression):
        if self.initialized:
            node.transpiler.warnings.error(node, f"Cannot reassign invariable '{self.name}'")

        return super().assign(node, expression)
