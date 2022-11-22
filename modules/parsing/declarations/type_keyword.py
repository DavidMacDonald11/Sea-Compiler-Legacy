from lexing.token import TYPE_KEYWORDS
from ..node import PrimaryNode

class TypeKeyword(PrimaryNode):
    @classmethod
    def construct(cls):
        return cls(cls.parser.expecting_has(*TYPE_KEYWORDS))

    def transpile(self):
        e_type, c_type = TYPE_MAP[self.token.string]
        return self.transpiler.expression(e_type, f"__sea_type_{c_type}__")

INT_MAP = {f"int{2 ** x}": ("i64", f"i{2 ** x}") for x in range(3, 7)}
UINT_MAP = {f"nat{2 ** x}": ("u64", f"u{2 ** x}") for x in range(3, 7)}
FLOAT_MAP = {
    "real32": ("f64", "f32"),
    "real64": ("f64", "f64"),
    "real": ("fmax", "fmax"),
    "imag32": ("c64", "f32"),
    "imag64": ("c64", "f64"),
    "imag": ("cmax", "fmax"),
    "cplex32": ("c64", "c32"),
    "cplex64": ("c64", "c64"),
    "cplex": ("cmax", "cmax")
}

TYPE_MAP = INT_MAP | UINT_MAP | FLOAT_MAP | {
    "bool": ("u64", "u8"),
    "char": ("u64", "u8"),
    "int": ("imax", "imax"),
    "nat": ("umax", "umax")
}
