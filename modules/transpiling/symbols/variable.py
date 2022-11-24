from .identifier import Identifier

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
