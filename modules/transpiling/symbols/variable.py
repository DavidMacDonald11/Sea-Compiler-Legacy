from .identifier import Identifier
from ..expression import Expression, OwnershipExpression

class Variable(Identifier):
    @property
    def c_name(self):
        return f"__sea_var_{self.name}__"

    @property
    def c_access(self):
        return f"(*{self.c_name})" if self.ownership is not None else self.c_name

    def __init__(self, name, kind, table_number):
        self.initialized = False
        self.transfered = False
        self.fun_local = False
        self.ownership = None
        super().__init__(name, kind, table_number)

    def access(self, node):
        if self.transfered:
            node.transpiler.warnings.error(node, "Cannot use dead identifier after ownership swap")

        expression = Expression(self.kind, self.c_access)
        expression.identifiers += [self.name]

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
            expression.drop_imaginary(node)

        return expression.verify_assign(node, self.kind)

    def transfer(self, expression, operator):
        expression = OwnershipExpression(self, operator, self.kind, expression.string)
        self.transfered = (operator == "$")
        return expression.add("&")
