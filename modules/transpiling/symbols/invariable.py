from .variable import Variable

class Invariable(Variable):
    @property
    def c_name(self):
        return f"__sea_invar_{self.name}__"

    def access(self, node):
        result = super().access(node)
        result.invariable = True

        return result

    def assign(self, node, expression):
        if self.initialized:
            node.transpiler.warnings.error(node, f"Cannot reassign invariable '{self.name}'")

        return super().assign(node, expression)

    def transfer(self, expression, operator):
        expression = super().transfer(expression, operator)
        expression.invariable = True
        return expression
