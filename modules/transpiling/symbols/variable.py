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
        if not self.initialized:
            self.initialized = True
            self.ownership = expression.ownership

        if self.is_transfered:
            node.transpiler.warnings.error(node, "Cannot use dead identifier after ownership swap")

        if expression.e_type == "":
            node.transpiler.warnings.error(node, "Function call has no return value")

        if self.s_type == "str" and expression.e_type != "str":
            node.transpiler.warnings.error(node, "Cannot assign non-str value to str identifeir")

        if self.s_type != "str" and expression.e_type == "str":
            node.transpiler.warnings.error(node, "Cannot assign str value to non-str identifier")

        if self.s_type == "bool" and expression.e_type != "bool":
            node.transpiler.warnings.error(node, "".join((
                "Cannot assign non-bool value to bool identifier. ",
                "(Consider using the '?' operator to get boolean value)"
            )))

        if self.s_type not in ("imag32", "imag64", "imag"):
            return expression

        return expression.drop_imaginary(node)
