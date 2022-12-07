from transpiling.expression import Expression, OwnershipExpression
from transpiling.symbols.function import Function, FunctionKind
from .primary_expression import Identifier
from ..node import Node

class PostfixCallExpression(Node):
    @property
    def nodes(self) -> list:
        return [self.expression] if self.arguments is None else [self.expression, self.arguments]

    def __init__(self, arguments):
        self.arguments = arguments
        self.expression = None

    @classmethod
    def construct(cls):
        arguments = ArgumentExpressionList.construct()
        cls.parser.expecting_has(")")
        return cls(arguments)

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

        return arg, FunctionKind(qualifier, arg.kind, arg.arrays, borrow)

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

        args = (qualifier, expression.kind, expression.arrays, borrow, defaults)
        return expression, FunctionKind(*args)
