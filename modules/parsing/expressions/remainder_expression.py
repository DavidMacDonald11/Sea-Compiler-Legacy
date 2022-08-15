from .unary_expression import UnaryExpression
from .bitwise_or_expression import BitwiseOrExpression
from ..node import BinaryOperation

class RemainderExpression(BinaryOperation):
    wrote = []

    @classmethod
    def construct(cls):
        return cls.construct_binary(["mod"], BitwiseOrExpression)

    def transpile(self):
        le_type, left = self.left.transpile()
        re_type, right = self.right.transpile()
        e_type = self.transpiler.resolve_type(le_type, re_type)

        if e_type in ("f64", "fmax"):
            self.transpiler.include("math")
            func = "fmod" if e_type == "f64" else "fmodl"
            return (e_type, f"({func}({left}, {right}))")

        if e_type in ("c64", "cmax"):
            self.transpiler.include("complex")
            self.transpiler.include("math")

            func = self.write_mod_func(e_type)
            return (e_type, f"({func}({left}, {right}))")

        return (e_type, f"{left} % {right}")

    def write_mod_func(self, e_type):
        func = f"__sea_func_mod_{e_type}__"

        if func in type(self).wrote: return func
        type(self).wrote += [func]

        round_func = UnaryExpression.write_round_func(self.transpiler, "floor", e_type)
        e_type = self.transpiler.safe_type(e_type)

        self.transpiler.header("\n".join((
            f"{e_type} {func}({e_type} left, {e_type} right)", "{",
            f"\treturn left - right * {round_func}(left / right);", "}\n"
        )))

        return func
