from lexing.token import POSTFIX_UNARY_OPERATORS
from transpiling.symbols.function import Function
from .primary_expression import PrimaryExpression, Identifier
from ..declarations.type_keyword import TYPE_MAP
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
        if not isinstance(self.expression, Identifier):
            self.transpiler.warnings.error(self, "Cannot call a non-function")
            return self.transpiler.expression("", f"/*{self.expression.transpile()}(...)*/")

        name = self.expression.token.string
        function = self.transpiler.symbols.at(self, name)

        if isinstance(function, Function):
            arguments = function.call(self, self.nodes[1])
            e_type = TYPE_MAP[function.return_type][0] if function.return_type is not None else ""
            return self.transpiler.expression("", f"{function.c_name}({arguments})").cast(e_type)

        if function is not None:
            self.transpiler.warnings.error(self, "Cannot call a non-function")

        return self.transpiler.expression("", f"/*{self.expression.transpile()}(...)*/")

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
        statement = None

        for i in range(len(self.arguments)):
            arg = self.arguments[i].transpile()
            p_qualifier, p_keyword, p_borrow = parameters[i]
            p_keyword = TYPE_MAP[p_keyword][0]

            a_qualifier = "invar" if arg.is_invar else "var"
            a_borrow = arg.ownership

            self.compare_borrow(i, p_borrow, a_borrow)
            self.check_var_borrow(i, a_borrow, p_borrow, a_qualifier, p_qualifier)
            self.compare_types(i, arg, p_keyword)

            statement = arg if statement is None else statement.new(f"%s, {arg}")
        return statement

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
        expression = self.transpiler.expression(p_keyword)
        expression = self.transpiler.expression.resolve(arg, expression)

        if expression.e_type == p_keyword:
            return

        message = f"Parameter {i + 1} requires {p_keyword}; found {arg.e_type}"
        self.transpiler.warnings.error(self, message)
