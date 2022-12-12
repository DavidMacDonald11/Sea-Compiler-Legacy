from .symbols.label import Label
from .symbols.variable import Variable
from .symbols.invariable import Invariable
from .symbols.function import Function, StandardFunction, MainFunction

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
            message = f"Reference to undeclared identifier '{key}'"
            raise node.transpiler.warnings.fail(node, message)

        return result

    def safe_at(self, node, key):
        if key in self.symbols:
            return self.symbols[key]

        return self.parent.safe_at(node, key) if self.parent is not None else None

    def verify_called_functions(self):
        for name, symbol in self.symbols.items():
            if not isinstance(symbol, Function): continue

            if symbol.caller is not None and not symbol.defined:
                if isinstance(symbol, StandardFunction):
                    symbol.define()
                    symbol.defined = True
                    continue

                message = f"Called function '{name}' has no definition"
                symbol.caller.transpiler.warnings.error(symbol.caller, message)

    def _new_symbol(self, cls, node, name, *args, **kwargs):
        if name in self.symbols:
            message = f"Cannot declare identifier '{name}' twice"
            node.transpiler.warnings.error(node, message)
            return None

        self.symbols[name] = identifier = cls(name, *args, **kwargs)
        return identifier

    def new_label(self, node, name):
        return self._new_symbol(Label, node, name)

    def new_variable(self, node, name, kind):
        return self._new_symbol(Variable, node, name, kind, self.number)

    def new_invariable(self, node, name, kind):
        return self._new_symbol(Invariable, node, name, kind, self.number)

    def new_function(self, node, name):
        if name in self.symbols:
            function = self.symbols[name]

            if not function.defined:
                return function

            node.transpiler.warnings.error(node, f"Cannot redefine function '{name}'")
            return None

        return self._new_symbol(Function if name != "main" else MainFunction, node, name)

    def new_standard_function(self, r_type, name, parameters, define):
        func = self._new_symbol(StandardFunction, None, name)
        func.return_type = r_type
        func.parameters = parameters
        func.define = define
        func.declared = True
