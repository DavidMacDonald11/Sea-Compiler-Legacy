from lexing.token import POSTFIX_UNARY_OPERATORS
from transpiling.expression import Expression, OwnershipExpression, FLOATING_TYPES
from transpiling.symbols.function import Function
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
        expression = self.expression.transpile().operate(self)

        if expression.kind != "bool":
            expression.add("(", " != 0)").cast("bool")

        return expression

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
        arguments = []

        while not cls.parser.next.has(")", r"\n", "EOF"):
            arguments += [cls.parser.expression.construct()]

            if cls.parser.next.has(","):
                cls.parser.take()

        return None if len(arguments) == 0 else cls(arguments)

    def transpile(self):
        raise NotImplementedError(type(self).__name__)

    def transpile_parameters(self, parameters):
        expression = None

        for i, (argument, parameter) in enumerate(zip(self.arguments, parameters)):
            arg = argument.transpile()
            p_qualifier, p_keyword, p_borrow = parameter

            if isinstance(arg, OwnershipExpression):
                a_qualifier = "invar" if arg.invariable else "var"
                a_borrow = arg.operator
            else:
                a_qualifier = "var"
                a_borrow = None

            self.compare_borrow(i, p_borrow, a_borrow)
            self.check_var_borrow(i, a_borrow, p_borrow, a_qualifier, p_qualifier)
            self.compare_types(i, arg, p_keyword)

            if "cplex" not in p_keyword:
                arg.drop_imaginary(self)

            expression = arg if expression is None else expression.add(after = f", {arg}")
        return expression

    def compare_borrow(self, i, p_borrow, a_borrow):
        if a_borrow == p_borrow:
            return

        p_kind = "borrow" if p_borrow == "&" else "ownership" if p_borrow == "$" else "value"
        a_kind = "borrow" if a_borrow == "&" else "ownership" if a_borrow == "$" else "value"

        message = f"Parameter {i + 1} requires {p_kind}; found {a_kind}"
        self.transpiler.warnings.error(self, message)

    def check_var_borrow(self, i, a_borrow, p_borrow, a_qualifier, p_qualifier):
        if a_borrow is None or a_qualifier == "var" or a_qualifier == p_qualifier:
            return

        p_kind = "borrow" if p_borrow == "&" else "ownership" if p_borrow == "$" else "value"
        message = f"Parameter {i + 1} requires variable {p_kind}; found invariable"
        self.transpiler.warnings.error(self, message)

    def compare_types(self, i, arg, p_keyword):
        expression = Expression.resolve(arg, Expression(p_keyword), allow_str = True)

        if expression.kind == p_keyword:
            return

        message = f"Parameter {i + 1} requires {p_keyword}; found {arg.kind}"
        self.transpiler.warnings.error(self, message)
