from lexing.token import POSTFIX_UNARY_OPERATORS
from transpiling.expression import Expression, OwnershipExpression, FLOATING_TYPES
from transpiling.symbols.function import Function, FunctionKind
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

class CallExpression(PostfixExpression):
    @property
    def nodes(self) -> list:
        return [self.expression] if self.arguments is None else [self.expression, self.arguments]

    def __init__(self, expression, arguments):
        self.arguments = arguments
        super().__init__(expression, arguments)

    def transpile(self):
        if not isinstance(self.expression, Identifier):
            self.transpiler.warnings.error(self, "Cannot call a non-function")
            return Expression("", f"/*{self.expression.transpile()}(...)*/")

        name = self.expression.token.string
        function = self.transpiler.symbols.at(self, name)

        if not isinstance(function, Function):
            self.transpiler.warnings.error(self, "Cannot call a non-function")
            return Expression("", f"/*{self.expression.transpile()}(...)*/")

        return function.call(self, self.arguments)

class ArgumentExpressionList(Node):
    @property
    def nodes(self) -> list:
        return self.arguments

    def __init__(self, arguments):
        self.arguments = arguments

    @classmethod
    def construct(cls):
        positional = True
        arguments = []

        while not cls.parser.next.has(")", r"\n", "EOF"):
            arguments += [FunctionArgument.construct()]

            if arguments[-1].identifier is None and not positional:
                message = "Positional argument cannot follow keyword argument"
                cls.parser.warnings.error(arguments[-1], message)

            positional = arguments[-1].identifier is None

            if cls.parser.next.has(","):
                cls.parser.take()

        return None if len(arguments) == 0 else cls(arguments)

    def transpile(self):
        raise NotImplementedError(type(self).__name__)

    def transpile_parameters(self, parameters):
        expression = None

        for i, (argument, parameter) in enumerate(zip(self.arguments, parameters)):
            arg, argument = argument.transpile()
            parameter.verify_arg(self, argument, i)

            if "cplex" not in parameter.kind:
                arg.drop_imaginary(self)

            expression = arg if expression is None else expression.add(after = f", {arg}")
        return expression

    def initialize_arg(self, argument):
        arg = argument.transpile()

        if isinstance(arg, OwnershipExpression):
            qualifier = "invar" if arg.invariable else "var"
            borrow = arg.operator
        else:
            qualifier = "var"
            borrow = None

        return arg, FunctionKind(qualifier, arg.kind, borrow)

class FunctionArgument(Node):
    @property
    def nodes(self):
        nodes = [self.expression]

        if self.identifier is not None:
            nodes = [self.identifier, self.expression]

        return nodes

    @property
    def defaults(self):
        return self.identifier

    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression

    @classmethod
    def construct(cls):
        identifier = None
        expression = cls.parser.expression.construct()

        if cls.parser.next.has("="):
            if not expression.of(Identifier):
                message = "Cannot assign value to non-keyword argument"
                cls.parser.warnings.error(cls.parser.take(), message)
            else:
                cls.parser.take()
                identifier = expression
                expression = cls.parser.expression.construct()

        return cls(identifier, expression)

    def transpile(self):
        identifier = self.identifier

        if identifier is not None:
            identifier = identifier.token.string

        expression = self.expression.transpile()
        defaults = (identifier, expression)

        if isinstance(expression, OwnershipExpression):
            qualifier = "invar" if expression.invariable else "var"
            borrow = expression.operator
        else:
            qualifier = "var"
            borrow = None

        return expression, FunctionKind(qualifier, expression.kind, borrow, defaults)
