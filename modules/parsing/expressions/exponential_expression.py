from transpiling.expression import Expression
from .postfix_expression import PostfixExpression
from ..node import BinaryOperation

class ExponentialExpression(BinaryOperation):
    @classmethod
    def construct(cls):
        return cls.construct_binary(["^"], PostfixExpression, cls.parser.unary_expression)

    def transpile(self):
        left = self.left.transpile().operate(self)
        right = self.right.transpile().operate(self)
        result = Expression.resolve(left, right).cast_up().new(f"({left}, {right})")

        if result.kind in ("int", "nat", "real"):
            self.transpiler.include("math")
            return result.add(f"(({result.kind})powl", ")")

        if any(map(lambda x: x in result.kind, ("int", "nat", "real"))):
            self.transpiler.include("math")
            return result.add(f"(({result.kind})pow", ")")

        if result.kind in ("imag", "cplex"):
            self.transpiler.include("tgmath")
            return result.add("(cpowl", ")").cast("cplex")

        if any(map(lambda x: x in result.kind), ("imag", "cplex")):
            self.transpiler.include("complex")
            return result.add("(cpow", ")").cast_replace("imag", "cplex")

        raise NotImplementedError(f"ExponentialExpression of {result.kind}")
