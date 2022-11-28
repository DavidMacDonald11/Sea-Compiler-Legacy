from .variable import Variable

class Invariable(Variable):
    @property
    def c_name(self):
        return f"__sea_invar_{self.name}__"

    def access(self, node, expression):
        result = super().access(node, expression)
        result.is_invar = True

        return result

    def assign(self, node, expression):
        if self.initialized:
            node.transpiler.warnings.error(node, f"Cannot reassign invariable '{self.name}'")

        return super().assign(node, expression)

    def transfer(self, node, expression, operator):
        expression.is_invar = True
        return super().transfer(node, expression, operator)
