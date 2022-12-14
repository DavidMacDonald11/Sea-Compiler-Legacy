from .statement import Statement
from .symbols.label import Label
from .symbols.variable import Variable
from .symbols.invariable import Invariable
from .symbols.function import Function, StandardFunction, MainFunction
from .utils import util, new_util

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

    def free(self, until = None):
        statement = Statement()

        if until is None:
            until = self

        for _, symbol in self.symbols.items():
            if not isinstance(symbol, (Variable, Invariable)) or symbol.transfered: continue

            if symbol.heap and symbol.ownership == "$":
                symbol.transfered = True

                if symbol.kind == "str" or symbol.arrays > 0:
                    free = util("free_array")
                    prefix = Statement().new(f"{free}({symbol.c_name}, {symbol.arrays})")
                    statement.new_append(prefix)

                statement.new_append(Statement().new(f"free({symbol.c_name})"))

        if self is not until:
            return statement.new_append(self.parent.free(until)).drop()

        return statement

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

    @new_util("free_array")
    @staticmethod
    def util_free_array(func):
        return "\n".join((
            f"void {func}(__sea_type_array__ *arr, __sea_type_nat__ dim)", "{",
            "\tif(dim < 2)", "\t{",
            "\t\tfree(arr->data);", "\t\treturn;", "\t}", "",
            "\tfor(__sea_type_nat__ i = 0; i < arr->size; i++)", "\t{",
            f"\t\t{func}(&((__sea_type_array__ *)arr->data)[i], dim - 1);", "\t}", "}"
        ))
