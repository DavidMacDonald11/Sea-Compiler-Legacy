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
        self.heap = False
        self.arrays = 0
        super().__init__(name, kind, table_number)

    def access(self, node):
        if self.transfered:
            message = "Cannot access dead identifier after ownership swap"
            node.transpiler.warnings.error(node, message)

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
                if self.kind != expression.kind:
                    node.transpiler.warnings.error(node, "".join((
                        "Assignment to ownership/borrow must be of the exact same type ",
                        f"({expression.kind})"
                    )))

                self.ownership = expression.operator
                self.heap = expression.heap

        if self.transfered:
            message = "Cannot assign to dead identifier after ownership swap"
            node.transpiler.warnings.error(node, message)

        if expression.kind == "":
            node.transpiler.warnings.error(node, "Function call has no return value")

        if "imag" in self.kind:
            expression.drop_imaginary(node, any_kind = True)

        return expression.verify_assign(node, self)

    def transfer(self, expression, operator):
        expression = OwnershipExpression(self, operator, self.kind, expression.string)
        expression.arrays = self.arrays
        expression.heap = self.heap
        self.transfered = (operator == "$")

        return expression.add("&")
