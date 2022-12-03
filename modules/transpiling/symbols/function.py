from .symbol import Symbol
from ..expression import Expression, OwnershipExpression

class Function(Symbol):
    @property
    def c_name(self):
        return f"__sea_fun_{self.name}__"

    @property
    def kind(self):
        return self.return_type.kind if self.return_type is not None else ""

    def __init__(self, name):
        self.declared = False
        self.defined = False
        self.returned = False
        self.caller = None
        self.parameters = []
        self.return_type = None
        super().__init__(name)

    def define(self):
        self.defined = True

    def set_parameters(self, node, parameters):
        params = []

        if parameters is not None:
            for parameter in parameters.parameters:
                params += [parameter.transpile_qualifiers()]

        if not self.declared:
            self.parameters = params
            return

        message = "Function definition parameters conflict with previous function declaration"

        if len(params) != len(self.parameters):
            node.transpiler.warnings.error(node, message)
            return

        for param, parameter in zip(params, self.parameters):
            if param != parameter:
                node.transpiler.warnings.error(node, message)
                return

    def set_return_type(self, node, return_type):
        if return_type is not None:
            return_type = FunctionKind(*return_type.components)
        else:
            return_type = FunctionKind(None, None, None)

        if not self.declared:
            self.return_type = return_type
            return

        if self.return_type != return_type:
            message = "Function definition return type conflicts with previous function declaration"
            node.transpiler.warnings.error(node, message)

    def call(self, node, arguments):
        self.caller = self.caller or node

        arg_count = 0 if arguments is None else len(arguments.arguments)
        param_count = len(self.parameters)

        if arg_count != param_count:
            message = f"Function requires {param_count} parameters; found {arg_count} arguments"
            node.transpiler.warnings.error(node, message)

        if arguments is None or arg_count != param_count:
            return ""

        args = arguments.transpile_parameters(self.parameters)
        expression = Expression(self.kind, f"{self.c_name}({args})")

        return self.set_expression(expression)

    def return_expression(self):
        self.returned = True
        return self.set_expression(Expression(self.kind))

    def set_expression(self, expression):
        if self.kind == "":
            if "imag" in self.kind:
                expression.add("(", " * 1.0j)")

            return expression

        if self.return_type.borrow is None:
            if "imag" in self.kind:
                expression.add("(", " * 1.0j)")

            return expression

        borrow = self.return_type.borrow
        expression = OwnershipExpression(None, borrow, expression.kind, expression.string)
        expression.invariable = (self.return_type.qualifier != "var")

        return expression

class StandardFunction(Function):
    def __init__(self, name):
        self.define = None
        super().__init__(name)

class FunctionKind:
    @property
    def noun(self):
        return "borrow" if self.borrow == "&" else "ownership" if self.borrow == "$" else "value"

    def __init__(self, qualifier, kind, borrow):
        self.qualifier = qualifier or ("var" if borrow is None else "invar")
        self.kind = kind or ""
        self.borrow = borrow

    def __eq__(self, other):
        if not isinstance(other, FunctionKind):
            raise NotImplementedError(f"Cannot compare FunctionKind to {type(other).__name__}")

        result = (self.qualifier == other.qualifier)
        result = result and self.kind == other.kind
        result = result and self.borrow == other.borrow

        return result

    def verify_arg(self, node, arg, i):
        message = f"Parameter {i + 1}"

        self.verify_arg_qualifier(node, arg, message)
        self.verify_arg_borrow(node, arg, message)
        self.verify_arg_kind(node, arg, message)

    def verify_arg_qualifier(self, node, arg, message):
        if self.qualifier != arg.qualifier == "invar":
            message = f"{message} requires variable {self.noun}; found invariable {arg.noun}"
            node.transpiler.warnings.error(node, message)

    def verify_arg_borrow(self, node, arg, message):
        if self.borrow != arg.borrow:
            message = f"{message} requires {self.noun}; found {arg.noun}"
            node.transpiler.warnings.error(node, message)

    def verify_arg_kind(self, node, arg, message):
        expression1 = Expression(self.kind)
        expression2 = Expression(arg.kind)
        kind = Expression.resolve(expression1, expression2, allow_str = True).kind

        if kind != self.kind:
            message = f"{message} must be {self.kind}; found {arg.kind}"
            node.transpiler.warnings.error(node, message)
