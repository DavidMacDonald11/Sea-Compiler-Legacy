import re
from util.warnings import CompilerError
from .token import Token

class NumericConstant(Token):
    def validate(self, symbols):
        d_int = re.compile(r"^\d+$")
        n_int = re.compile(r"^\d+b[A-Z0-9]+$")
        d_float = re.compile(r"^\d*.?\d*(e[+-]?\d+)?$")
        dn_float =  re.compile(r"^\d*.?\d*(e[+-]?\d+b[A-Z0-9]+)?$")
        nd_float = re.compile(r"^\d+b[A-Z0-9]*.?[A-Z0-9]*(e[+-]?\d+)?$")
        n_float = re.compile(r"^\d+b[A-Z0-9]*.?[A-Z0-9]*(e[+-]?\d+b[A-Z0-9]+)?$")

        if d_int.match(symbols) or n_int.match(symbols):
            return

        if "." not in symbols and "e" not in symbols:
            raise CompilerError("Incorrect integer constant", self.string)

        is_float = d_float.match(symbols) or dn_float.match(symbols)
        is_float = is_float or nd_float.match(symbols) or n_float.match(symbols)

        if not is_float:
            raise CompilerError("Incorrect float constant", self.string)
