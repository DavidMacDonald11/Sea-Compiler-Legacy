from .identifier import Identifier

class Label(Identifier):
    @property
    def c_name(self):
        return f"__sea_label_{self.name}"

    def surround(self, node, expression):
        c_label = f"{self.c_name}_continue__:"
        b_label = f"{self.c_name}_break__:"

        return expression.new(f"{node.indent}{c_label}\n%s\n {node.indent}{b_label}")
