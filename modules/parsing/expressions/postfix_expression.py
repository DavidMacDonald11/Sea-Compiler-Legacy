from lexing.token import POSTFIX_UNARY_OPERATORS
from transpiling.symbol_table import Function
from .primary_expression import PrimaryExpression, Identifier
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

        if not cls.parser.next.has(*POSTFIX_UNARY_OPERATORS, "("):
            return node

        while cls.parser.next.has(*POSTFIX_UNARY_OPERATORS, "("):
            operator = cls.parser.take()

            match operator.string:
                case "%":
                    node = PercentExpression(node, operator)
                case "!":
                    node = FactorialExpression(node, operator)
                case "?":
                    node = TestExpression(node, operator)
                case "(":
                    arguments = ArgumentExpressionList.construct()
                    cls.parser.expecting_has(")")
                    node = CallExpression(node, arguments)

        return node

class PercentExpression(PostfixExpression):
    def transpile(self):
        expression = self.expression.transpile().operate(self)
        return expression.new("(%s / 100)").cast_up()

class FactorialExpression(PostfixExpression):
    wrote = []

    def transpile(self):
        expression = self.expression.transpile().operate(self)

        if expression.e_type in ("f64", "fmax", "c64", "cmax"):
            self.transpiler.warnings.error(self, "Cannot use factorial on floating type")
            return expression.new("%s/*!*/")

        largest = expression.e_type in ("imax", "umax")
        func = self.write_func(expression.cast("u64" if largest else "umax"))
        return expression.new(f"({func}(%s))")

    def write_func(self, expression):
        func = f"__sea_func_factorial_{expression.e_type}__"

        if func in type(self).wrote: return func
        type(self).wrote += [func]

        e_type = expression.c_type

        self.transpiler.header("\n".join((
            f"{e_type} {func}({e_type} num)", "{",
            f"\t{e_type} result = 1;",
            f"\tfor({e_type} i = 2; i <= num; i++) result *= i;",
            "\treturn result;", "}\n"
        )))

        return func

class TestExpression(PostfixExpression):
    def transpile(self):
        expression = self.expression.transpile().operate(self)
        return expression.new("%s" if expression.e_type == "bool" else "(%s != 0)").cast("bool")

class CallExpression(PostfixExpression):
    def transpile(self):
        arguments = self.nodes[1].transpile() if self.nodes[1] is not None else ""

        if not isinstance(self.expression, Identifier):
            self.transpiler.warnings.error(self, "Cannot call a non-function")
            return self.transpiler.expression("", f"/*{self.expression.transpile()}({arguments})*/")

        name = self.expression.token.string
        function = self.transpiler.symbols.at(self, name)

        if isinstance(function, Function):
            return self.transpiler.expression("", f"{function.c_name}({arguments})")

        if function is not None:
            self.transpiler.warnings.error(self, "Cannot call a non-function")

        return self.transpiler.expression("", f"/*{self.expression.transpile()}({arguments})*/")

class ArgumentExpressionList(Node):
    @property
    def nodes(self) -> list:
        return self.arguments

    def __init__(self, arguments):
        self.arguments = arguments

    @classmethod
    def construct(cls):
        arguments = []

        while not cls.parser.next.has(")", r"\n", "EOF"):
            arguments += [cls.parser.expression.construct()]

            if cls.parser.next.has(","):
                cls.parser.take()

        return None if len(arguments) == 0 else cls(arguments)

    def transpile(self):
        first, *arguments = self.arguments
        statement = first.transpile()

        for argument in arguments:
            statement = statement.new(f"%s, {argument.transpile()}")

        return statement
