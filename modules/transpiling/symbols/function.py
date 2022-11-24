from .identifier import Identifier

class Function(Identifier):
    @property
    def c_name(self):
        return f"__sea_fun_{self.name}__"

    def __init__(self, s_type, name, table_number):
        self.declared = False
        self.defined = False
        self.caller = None
        self.parameters = []
        self.return_type = None
        super().__init__(s_type, name, table_number)

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

        for i in range(len(params)):
            if params[i] != self.parameters[i]:
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

        return arguments.transpile_parameters(self.parameters)

    def set_return_type(self, node, return_type):
        return_type = return_type.token.string if return_type is not None else None

        if not self.declared:
            self.return_type = return_type
            return

        if self.return_type != return_type:
            message = "Function definition return type conflicts with previous function declaration"
            node.transpiler.warnings.error(node, message)
