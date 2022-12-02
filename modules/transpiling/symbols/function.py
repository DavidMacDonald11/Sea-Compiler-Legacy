from .symbol import Symbol
from ..expression import Expression, OwnershipExpression

class Function(Symbol):
    @property
    def c_name(self):
        return f"__sea_fun_{self.name}__"

    @property
    def kind(self):
        return self.return_type[1] if self.return_type is not None else ""

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

    def set_return_type(self, node, return_type):
        if return_type is not None:
            return_type = return_type.components

        if not self.declared:
            self.return_type = return_type
            return

        if self.return_type != return_type:
            message = "Function definition return type conflicts with previous function declaration"
            node.transpiler.warnings.error(node, message)

    def return_expression(self):
        self.returned = True
        return self.set_expression(Expression(self.kind))

    def set_expression(self, expression):
        if self.return_type is None:
            if "imag" in self.kind:
                expression.add("(", " * 1.0j)")

            return expression

        qualifier, _, borrow = self.return_type

        if borrow is None:
            if "imag" in self.kind:
                expression.add("(", " * 1.0j)")

            return expression

        expression = OwnershipExpression(None, borrow, expression.kind, expression.string)
        expression.invariable = (qualifier != "var")

        return expression

class StandardFunction(Function):
    def __init__(self, name):
        self.define = None
        super().__init__(name)
