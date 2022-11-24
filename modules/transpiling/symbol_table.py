from .symbols.label import Label
from .symbols.variable import Variable
from .symbols.invariable import Invariable
from .symbols.function import Function

class SymbolTable:
    count = 0

    def __init__(self, parent = None):
        type(self).count += 1

        self.symbols = {}
        self.parent = parent
        self.number = type(self).count

    def __repr__(self):
        if self.parent is None:
            return f"{self.number} {self.symbols}"

        return f"{self.parent},\n    {self.number} {self.symbols}"

    def at(self, node, key):
        result = self.safe_at(node, key)

        if result is None:
            node.transpiler.warnings.error(node, f"Reference to undeclared identifier '{key}'")

        return result

    def safe_at(self, node, key):
        if key in self.symbols:
            return self.symbols[key]

        return self.parent.safe_at(node, key) if self.parent is not None else None

    def verify_called_functions(self):
        for name, symbol in self.symbols.items():
            print(symbol.caller if isinstance(symbol, Function) else "")

            if isinstance(symbol, Function) and symbol.caller is not None and not symbol.defined:
                message = f"Called function '{name}' has no definition"
                symbol.caller.transpiler.warnings.error(symbol.caller, message)

    def _new_identifier(self, cls, node, s_type, name):
        if name in self.symbols:
            message = f"Cannot declare identifier '{name}' twice."
            node.transpiler.warnings.error(node, message)
            return None

        self.symbols[name] = identifier = cls(s_type, name, self.number)
        return identifier

    def new_label(self, node, name):
        return self._new_identifier(Label, node, None, name)

    def new_variable(self, node, s_type, name):
        return self._new_identifier(Variable, node, s_type, name)

    def new_invariable(self, node, s_type, name):
        return self._new_identifier(Invariable, node, s_type, name)

    def new_function(self, node, s_type, name):
        if name in self.symbols:
            function = self.symbols[name]

            if not function.defined:
                return function

        return self._new_identifier(Function, node, s_type, name)
