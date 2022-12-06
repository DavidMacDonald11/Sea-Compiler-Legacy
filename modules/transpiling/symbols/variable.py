from .identifier import Identifier
from ..expression import Expression, OwnershipExpression

class Variable(Identifier):
    @property
    def c_name(self):
        return f"__sea_var_{self.name}__"

    @property
    def c_access(self):
        name = self.c_name

        if self.ownership is not None:
            name = f"(*{name})"

        return name

    def __init__(self, name, kind, table_number):
        self.initialized = False
        self.transfered = False
        self.fun_local = False
        self.ownership = None
        self.arrays = 0
        super().__init__(name, kind, table_number)

    def access(self, node):
        if self.transfered:
            node.transpiler.warnings.error(node, "Cannot use dead identifier after ownership swap")

        expression = Expression(self.kind, self.c_access)
        expression.identifiers += [self.name]
        expression.arrays = self.arrays

        if self.initialized:
            return expression

        node.transpiler.warnings.error(node, f"Accessing uninitialized identifier '{self.name}'")
        return expression.add("/*", "*/")

    def assign(self, node, expression):
        if not self.initialized:
            self.initialized = True
            self.fun_local = node.transpiler.context.in_function

            if isinstance(expression, OwnershipExpression):
                self.ownership = expression.operator

        if self.transfered:
            node.transpiler.warnings.error(node, "Cannot use dead identifier after ownership swap")

        if expression.kind == "":
            node.transpiler.warnings.error(node, "Function call has no return value")

        if "imag" in self.kind:
            expression.drop_imaginary(node, any_kind = True)

        if expression.arrays != self.arrays:
            e_title = f"{expression.arrays}D array" if expression.arrays > 0 else "non-array"
            s_title = f"{self.arrays}D array" if self.arrays > 0 else "non-array"
            node.transpiler.warnings.error(node, f"{e_title} cannot be assigned to {s_title}")

        return expression.verify_assign(node, self.kind)

    def transfer(self, expression, operator):
        expression = OwnershipExpression(self, operator, self.kind, expression.string)
        expression.arrays = self.arrays
        self.transfered = (operator == "$")

        return expression.add("&")
