from transpiling.expression import Expression
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
        result = Expression.resolve(left, right).cast_up()

        if "real" in result.kind:
            self.transpiler.include("math")
            func = "fmod" if result.kind != "real" else "fmodl"
            return result.new(f"{func}({left}, {right})")

        if any(map(lambda x: x in result.kind, ("imag", "cplex"))):
            self.transpiler.include("complex")
            self.transpiler.include("math")

            if "imag" in result.kind :
                result.cast(result.kind.replace("imag", "cplex"))

            func = self.write_func(result.kind)
            return result.new(f"{func}({left}, {right})")

        return result.new(f"({left}) % ({right})")

    def write_func(self, kind):
        func = f"__sea_func_mod_{kind}__"

        if func in type(self).wrote: return func
        type(self).wrote += [func]

        round_func = RoundExpression.write_func(self.transpiler, "floor", kind)
        kind = f"__sea_type_{kind}"

        self.transpiler.header("\n".join((
            f"{kind} {func}({kind} left, {kind} right)", "{",
            f"\treturn left - right * {round_func}(left / right);", "}\n"
        )))

        return func
