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

        if self.name == "main":
            message = "Main function must be declared 'fun main(str[] args) -> int'"
        else:
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
            return_type = FunctionKind(None, None, 0, None)

        if not self.declared:
            self.return_type = return_type
            return

        if self.return_type != return_type:
            message = "Function definition return type conflicts with previous function declaration"
            node.transpiler.warnings.error(node, message)

    def call(self, node, arguments):
        self.caller = self.caller or node
        arguments = [] if arguments is None else arguments.arguments

        args = FunctionKind.verify_args(node, self.parameters, arguments)
        expression = Expression(self.kind, f"{self.c_name}({args})")
        expression.identifiers += [self.name]

        return self.set_expression(expression)

    def return_expression(self):
        self.returned = True
        return self.set_expression(Expression(self.kind))

    def set_expression(self, expression):
        expression.arrays = self.return_type.arrays

        if self.kind == "":
            if "imag" in self.kind:
                expression.add("(", " * 1.0j)")

            return expression

        if self.return_type.borrow is None:
            if "imag" in self.kind:
                expression.add("(", " * 1.0j)")

            return expression

        args = (self.return_type.borrow, expression.kind, expression.string, expression.arrays)
        expression = OwnershipExpression(None, *args)
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

    def __init__(self, qualifier, kind, arrays, borrow, defaults = None):
        self.qualifier = qualifier or ("var" if borrow is None else "invar")
        self.kind = kind or ""
        self.arrays = arrays or 0
        self.borrow = borrow
        self.defaults = defaults
        self.arg = None

    def __eq__(self, other):
        if not isinstance(other, FunctionKind):
            raise NotImplementedError(f"Cannot compare FunctionKind to {type(other).__name__}")

        result = (self.qualifier == other.qualifier)
        result = result and self.kind == other.kind or other.kind == "any"
        result = result and self.arrays == other.arrays
        result = result and self.borrow == other.borrow
        result = result and self.defaults == other.defaults

        return result

    @classmethod
    def verify_args(cls, node, params, args):
        pos_params, key_params = cls.split_positional(params)
        pos_args, key_args = cls.split_positional(args)

        if len(pos_args) < len(pos_params):
            p_count = len(pos_params)
            a_count = len(pos_args)

            p_noun = "positional " + ("parameter" if p_count == 1 else "parameters")
            a_noun = "positional " + ("argument" if a_count == 1 else "arguments")

            message = f"Function requires {p_count} {p_noun}; found {a_count} {a_noun}"
            node.transpiler.warnings.error(node, message)
            return Expression()

        key_args += pos_args[len(pos_params):]
        pos_args = pos_args[:len(pos_params)]

        expression = cls.verify_positional_args(node, pos_params, pos_args)
        expression2 = cls.verify_keyword_args(node, key_params, key_args, len(pos_params))

        for param in params:
            param.arg = None

        if expression.string == "":
            expression = expression2
        elif expression2.string != "":
            expression.add(after = f", {expression2}")

        return expression

    @classmethod
    def split_positional(cls, kinds):
        positional = []
        keyword = []

        for kind in kinds:
            if kind.defaults is None:
                positional += [kind]
            else:
                keyword += [kind]

        return positional, keyword

    @classmethod
    def verify_positional_args(cls, node, params, args):
        expression = None

        for i, (arg, param) in enumerate(zip(args, params)):
            arg_exp, arg_kind = arg.transpile()
            param.verify_arg(node, arg_exp, arg_kind, i)

            if "cplex" not in param.kind:
                arg_exp.drop_imaginary(node)

            expression = arg_exp if expression is None else expression.add(after = f", {arg_exp}")

        return expression or Expression()

    @classmethod
    def verify_keyword_args(cls, node, params, args, pos_count):
        expression = None
        original = params

        for i, arg in enumerate(args):
            arg_exp, arg_kind = arg.transpile()

            if arg.identifier is None:
                data = (node, params, arg_exp, arg_kind, pos_count + i)
                params = cls.match_positional_to_keyword(*data)

                if params is None: break
            else:
                cls.match_keywords(node, original, arg_exp, arg_kind, pos_count + i)

        for param in original:
            arg = param.arg or param.defaults[1].copy()

            if "cplex" not in param.kind:
                arg.drop_imaginary(node)

            expression = arg if expression is None else expression.add(after = f", {arg}")

        return expression or Expression()

    @classmethod
    def match_positional_to_keyword(cls, node, params, arg_exp, arg_kind, pos_count):
        if len(params) == 0:
            node.transpiler.warnings.error(node, "Too many function arguments provided")
            return None

        param, *params = params
        param.verify_arg(node, arg_exp, arg_kind, pos_count)
        return params

    @classmethod
    def match_keywords(cls, node, params, arg_exp, arg_kind, pos_count):
        identifier = arg_kind.defaults[0]
        param = cls.param_at(node, params, identifier)

        if param is not None:
            param.verify_arg(node, arg_exp, arg_kind, pos_count)

    @classmethod
    def param_at(cls, node, params, key):
        for param in params:
            if param.defaults[0] == key:
                return param

        message = f"No such keyword argument as '{key}'"
        node.transpiler.warnings.error(node, message)
        return None

    def verify_arg(self, node, arg_exp, arg, i):
        if self.arg is not None:
            message = f"Multiple values given for argument '{self.defaults[0]}'"
            node.transpiler.warnings.error(node, message)
            return

        message = f"Parameter {i + 1}"

        self.verify_arg_qualifier(node, arg, message)
        self.verify_arg_borrow(node, arg, message)

        if self.kind != "any":
            self.verify_arg_kind(node, arg, message)
            self.verify_arg_dimensions(node, arg, message)

        self.arg = arg_exp

    def verify_arg_qualifier(self, node, arg, message):
        if self.qualifier != arg.qualifier == "invar":
            message = f"{message} requires variable {self.noun}; found invariable {arg.noun}"
            node.transpiler.warnings.error(node, message)

    def verify_arg_borrow(self, node, arg, message):
        print(self.borrow, arg.borrow)

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

    def verify_arg_dimensions(self, node, arg, message):
        if self.arrays != arg.arrays:
            a_title = f"{arg.arrays}D array" if arg.arrays > 0 else "non-array"
            s_title = f"{self.arrays}D array" if self.arrays > 0 else "non-array"
            message = f"{message} requires {s_title}; found {a_title}"
            node.transpiler.warnings.error(node, message)
