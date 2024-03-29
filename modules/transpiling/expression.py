class Expression:
    @property
    def format_tag(self):
        return FORMAT_TAGS[self.kind]

    def __init__(self, kind = "", string = ""):
        self.kind = kind
        self.string = string
        self.identifiers = []
        self.finished = False
        self._show_kind = False

    def __eq__(self, other):
        return self.string == other.string

    def __repr__(self):
        return self.string

    def copy(self):
        other = Expression(self.kind, self.string)
        other.identifiers = self.identifiers
        other.finished = self.finished
        if self._show_kind: other.show_kind()

        return other

    def show_kind(self):
        self._show_kind = True
        return self

    def finish(self, node, semicolons):
        if self.finished: return self
        self.finished = True

        indent = "\t" * node.transpiler.context.blocks
        end = ";" if semicolons else ""
        end = f"{end} /*{self.kind}*/" if self._show_kind else end

        return self.add(indent, end)

    def new(self, string):
        self.string = string
        return self

    def add(self, before = "", after = ""):
        self.string = f"{before}{self.string}{after}"
        return self

    def cast(self, kind):
        self.kind = kind
        return self

    def cast_up(self):
        self.kind = "nat8" if self.kind in ("bool", "char") else self.kind
        return self

    def drop_imaginary(self, node):
        if "imag" not in self.kind: return self

        node.transpiler.include("complex")
        return self.add(f"cimag{'l' if self.kind == 'imag' else ''}(", ")")

    def operate(self, node, bitwise = False, boolean = False):
        if self.kind in ("str", "list"):
            node.transpiler.warnings.error(node, f"Cannot perform operation on {self.kind} (yet)")

        if bitwise and self.kind in FLOATING_TYPES:
            message = "Cannot perform bitwise operation on floating type"
            node.transpiler.warnings.error(node, message)

        if boolean and self.kind != "bool":
            node.transpiler.warnings.error(node, "".join((
                "Conditional value must be of type 'bool'. ",
                "(Consider using the '?' operator to get a boolean value)"
            )))

        return self

    def assert_constant(self, node):
        if len(self.identifiers) > 0:
            node.transpiler.warnings.error(node, "Expression must be a constant expression")

        return self

    def verify_assign(self, node, kind):
        if self.kind == "str" and kind != "str":
            node.transpiler.warnings.error(node, "Cannot assign non-str value to str identifier")

        if self.kind != "str" and kind == "str":
            node.transpiler.warnings.error(node, "Cannot assign str value to non-str identifier")

        if self.kind == "bool" and kind != "bool":
            node.transpiler.warnings.error(node, "".join((
                "Cannot assign non-bool value to bool identifier. ",
                "(Consider using the '?' operator to get boolean value)"
            )))

        return self

    @classmethod
    def resolve(cls, left, right, allow_str = False):
        kind1, kind2 = left.kind, right.kind

        if "imag" in kind1 and "imag" not in kind2:
            kind1 = kind1.replace("imag", "cplex")
        elif "imag" in kind2 and "imag" not in kind1:
            kind2 = kind2.replace("imag", "cplex")

        expression = cls(kind1 if POINTS[kind1] > POINTS[kind2] else kind2)
        expression.identifiers = left.identifiers + right.identifiers

        if not allow_str and expression.kind == "str":
            raise KeyError("String is not allowed in this context")

        return expression

FLOATING_TYPES = ("real32, real64, real, imag32, imag64, imag, cplex32, cplex64, cplex")

POINTS = {
    "bool": 0, "char": .5,
    "nat8": 1, "nat16": 2, "nat32": 3, "nat64": 4, "nat": 5,
    "int8": 1.5, "int16": 2.5, "int32": 3.5, "int64": 4.5, "int": 5.5,
    "real32": 6, "real64": 7, "real": 8, "imag32": 6, "imag64": 7, "imag": 8,
    "cplex32": 9, "cplex64": 10, "cplex": 11,
    "str": 100
}

FORMAT_TAGS = {
    "bool": "%s", "char": "%c",
    "nat8": "%hu", "nat16": "%hu", "nat32": "%u", "nat64": "%lu", "nat": "%lu",
    "int8": "%hd", "int16": "%hd", "int32": "%d", "int64": "%ld", "int": "%ld",
    "real32": "%f", "real64": "%lf", "real": "%Lf", "imag32": "%f", "imag64": "%lf", "imag": "%Lf",
    "cplex32": "%f", "cplex64": "%lf", "cplex": "%Lf",
    "str": "%s"
}

class OwnershipExpression(Expression):
    def __init__(self, owner, operator, kind = "", string = ""):
        self.owners = [owner, None]
        self.operator = operator
        self.invariable = False
        super().__init__(kind, string)

    def drop_imaginary(self, node):
        return self

    def operate(self, node, bitwise = False, boolean = False):
        node.transpiler.warnings.error(node, "Cannot perform operations on ownership rvalue")
        return self
