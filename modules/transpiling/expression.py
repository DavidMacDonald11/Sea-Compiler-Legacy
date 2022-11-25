from parsing.declarations.type_keyword import TYPE_MAP

class Expression:
    @property
    def c_type(self):
        return f"__sea_type_{self.e_type}__"

    def __init__(self, e_type = "", string = ""):
        self.string = string
        self.e_type = e_type
        self.ownership = None
        self.owners = [None, None]
        self.identifiers = []
        self.is_invar = False
        self.newline = False

    def __repr__(self):
        return self.string + ("\n" if self.newline else "")

    def copy(self):
        expression = Expression(self.e_type, self.string)
        expression.ownership = self.ownership
        expression.owners = self.owners.copy()
        expression.identifiers = self.identifiers.copy()
        expression.is_invar = self.is_invar

        return expression

    def new(self, string):
        self.string = string.replace("%s", self.string).replace("%e", self.e_type)
        return self

    def cast(self, e_type):
        self.e_type = TYPE_MAP[e_type][0] if e_type in TYPE_MAP and e_type != "bool" else e_type
        return self

    def cast_up(self):
        self.e_type = "u64" if self.e_type == "bool" else self.e_type
        return self

    def operate(self, node):
        if self.e_type == "":
            node.transpiler.warnings.error(node, "Function call has no return value")

        if self.ownership is not None:
            node.transpiler.warnings.error(node, "Cannot perform operations on ownership rvalue")

        return self

    def boolean(self, node):
        if self.e_type != "bool":
            node.transpiler.warnings.error(node, "".join((
                "Conditional value must be of type bool. ",
                "(Consider using the '?' operator to get boolean value)"
            )))

        return self

    def drop_imaginary(self, node):
        if self.e_type[0] != "g" or self.ownership is not None:
            return self

        node.transpiler.include("complex")
        return self.new(f"cimag{'' if self.e_type == 'g64' else 'l'}(%s)")

    @classmethod
    def resolve(cls, left, right):
        e_type1, e_type2 = left.e_type, right.e_type
        e_type = e_type1 if POINTS[e_type1] > POINTS[e_type2] else e_type2

        if e_type1[0] != e_type2[0] == "g" or e_type2[0] != e_type2[0] == "g":
            e_type = f"c{e_type[1:]}"

        expression = cls(e_type)
        expression.identifiers = left.identifiers + right.identifiers

        return expression


POINTS = {
    "": -1,
    "bool": 0,
    "u64": 1,
    "i64": 2,
    "umax": 2.25,
    "imax": 2.5,
    "f64": 3,
    "fmax": 3.5,
    "g64": 3,
    "gmax": 3.5,
    "c64": 4,
    "cmax": 4.5
}
