from parsing.declarations.type_keyword import TYPE_MAP

class Expression:
    @property
    def c_type(self):
        return f"__sea_type_{self.e_type}__"

    def __init__(self, e_type, string):
        self.string = string
        self.e_type = e_type
        self.ownership = None
        self.is_invar = False

    def __repr__(self):
        return self.string

    def new(self, string):
        self.string = string.replace("%s", self.string).replace("%e", self.e_type)
        return self

    def cast(self, e_type):
        self.e_type = TYPE_MAP[e_type][0] if e_type in TYPE_MAP else e_type
        return self

    def cast_up(self):
        self.e_type = "u64" if self.e_type == "bool" else self.e_type
        return self

    def operate(self, node):
        if self.ownership is not None:
            node.transpiler.warnings.error(node, "Cannot perform operations on ownership rvalue")

        return self

    @classmethod
    def resolve(cls, left, right):
        e_type1, e_type2 = left.e_type, right.e_type
        e_type = e_type1 if POINTS[e_type1] > POINTS[e_type2] else e_type2
        return cls(e_type, "")

POINTS = {
    "bool": 0,
    "u64": 1,
    "i64": 2,
    "umax": 2.25,
    "imax": 2.5,
    "f64": 3,
    "fmax": 3.5,
    "c64": 4,
    "cmax": 4.5
}
