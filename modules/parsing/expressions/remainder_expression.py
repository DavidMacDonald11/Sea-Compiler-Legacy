from transpiling.expression import Expression
from transpiling.utils import util, new_util
from .unary_expression import RoundExpression
from .cast_expression import CastExpression
from ..node import BinaryOperation

class RemainderExpression(BinaryOperation):
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
                result.cast_replace("imag", "cplex")

            func = util(self.util_mod(result.kind))
            return result.new(f"{func}({left}, {right})")

        return result.new(f"({left}) % ({right})")

    @staticmethod
    def util_mod(kind):
        name = f"mod_{kind}"

        @new_util(name)
        def func(func):
            floor = util(RoundExpression.util_round("floor", kind))
            kind = f"__sea_type_{kind}"

            return "\n".join((
                f"{kind} {func}({kind} left, {kind} right)", "{",
                f"\treturn left - right * {floor}(left / right);", "}\n"
            ))

        return name
