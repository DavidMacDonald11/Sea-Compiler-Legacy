from .unary_expression import RoundExpression
from .cast_expression import CastExpression
from ..node import BinaryOperation

class RemainderExpression(BinaryOperation):
    wrote = []

    @classmethod
    def construct(cls):
        return cls.construct_binary(["mod"], CastExpression)

    def transpile(self):
        left = self.left.transpile().operate(self)
        right = self.right.transpile().operate(self)
        result = self.transpiler.expression.resolve(left, right).cast_up()

        if result.e_type in ("f64", "fmax"):
            self.transpiler.include("math")
            func = "fmod" if result.e_type else "fmodl"
            return result.new(f"{func}({left}, {right})")

        if result.e_type in ("g64", "gmax", "c64", "cmax"):
            self.transpiler.include("complex")
            self.transpiler.include("math")

            if result.e_type[0] == "g":
                result.e_type = f"c{result.e_type[1:]}"

            func = self.write_func(result)
            return result.new(f"{func}({left}, {right})")

        return result.new(f"({left}) % ({right})")

    def write_func(self, expression):
        func = f"__sea_func_mod_{expression.e_type}__"

        if func in type(self).wrote: return func
        type(self).wrote += [func]

        round_func = RoundExpression.write_func(self.transpiler, "floor", expression)
        e_type = expression.c_type

        self.transpiler.header("\n".join((
            f"{e_type} {func}({e_type} left, {e_type} right)", "{",
            f"\treturn left - right * {round_func}(left / right);", "}\n"
        )))

        return func
