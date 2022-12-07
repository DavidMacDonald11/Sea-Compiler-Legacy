from lexing.token import POSTFIX_UNARY_OPERATORS
from transpiling.expression import FLOATING_TYPES
from .primary_expression import PrimaryExpression
from .postfix_call_expression import PostfixCallExpression
from .postfix_access_expression import PostfixAccessExpression
from ..node import Node

class PostfixExpression(Node):
    @property
    def nodes(self) -> list:
        return [self.expression, self.operator]

    def __init__(self, expression, operator):
        self.expression = expression
        self.operator = operator

    @classmethod
    def construct(cls):
        node = PrimaryExpression.construct()

        while cls.parser.next.has(*POSTFIX_UNARY_OPERATORS, "(", "["):
            operator = cls.parser.take()

            match operator.string:
                case "%":
                    node = PercentExpression(node, operator)
                case "!":
                    node = FactorialExpression(node, operator)
                case "?":
                    node = TestExpression(node, operator)
                case "(":
                    call_node = PostfixCallExpression.construct()
                    call_node.expression = node
                    node = call_node
                case "[":
                    access_node = PostfixAccessExpression.construct()
                    access_node.expression = node
                    node = access_node

        return node

class PercentExpression(PostfixExpression):
    def transpile(self):
        expression = self.expression.transpile().operate(self)
        return expression.add("(", " / 100)").cast_up()

class FactorialExpression(PostfixExpression):
    wrote = []

    def transpile(self):
        expression = self.expression.transpile().operate(self)

        if expression.kind in FLOATING_TYPES:
            self.transpiler.warnings.error(self, "Cannot use factorial on floating type")
            return expression.add(after = "/*!*/")

        if "int" in expression.kind:
            message = "Factorial of an integer, if negative, may produce unexpected results"
            self.transpiler.warnings.warn(self, message)

        expression.cast("nat")
        func = self.write_func()
        return expression.add(f"({func}(", "))")

    def write_func(self):
        func = "__sea_func_factorial__"

        if func in type(self).wrote: return func
        type(self).wrote += [func]

        kind = "__sea_type_nat__"

        self.transpiler.header("\n".join((
            f"{kind} {func}({kind} num)", "{",
            f"\t{kind} result = 1;",
            f"\tfor({kind} i = 2; i <= num; i++) result *= i;",
            "\treturn result;", "}\n"
        )))

        return func

class TestExpression(PostfixExpression):
    def transpile(self):
        expression = self.expression.transpile().operate(self, arrays = True)

        if expression.kind == "str" or expression.arrays > 0:
            expression.add(after = ".size")
            expression.arrays = 0
        elif expression.kind == "bool":
            return expression

        return expression.add("(", " != 0)").cast("bool")
