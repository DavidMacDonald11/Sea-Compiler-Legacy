from lexing.token import TYPE_KEYWORDS
from ..node import PrimaryNode

class TypeKeyword(PrimaryNode):
    @classmethod
    def construct(cls):
        return cls(cls.parser.expecting_has(*TYPE_KEYWORDS))

    def transpile(self):
        return f"__sea_type_{TYPE_MAP[self.token.string]}__"

INT_MAP = {f"int{2 ** x}": f"i{2 ** x}" for x in range(3, 7)}
UINT_MAP = {f"nat{2 ** x}": f"u{2 ** x}" for x in range(3, 7)}
FLOAT_MAP = {
    "real32": "f32",
    "real64": "f64",
    "real": "fmax",
    "imag32": "f32",
    "imag64": "f64",
    "imag": "fmax",
    "cplex32": "c32",
    "cplex64": "c64",
    "cplex": "cmax"
}

TYPE_MAP = INT_MAP | UINT_MAP | FLOAT_MAP | {
    "bool": "u8",
    "char": "u8",
    "int": "imax",
    "nat": "umax"
}
