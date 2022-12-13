from transpiling.statement import Statement
from transpiling.expression import Expression
from transpiling.symbols.function import FunctionKind
from lexing.token import TYPE_KEYWORDS, TYPE_MODIFIER_KEYWORDS
from .full_type import FullType
from ..node import Node

# TODO verify returns from all branches

class FunctionDeclaration(Node):
    @property
    def nodes(self) -> list:
        nodes = [self.identifier]

        if self.parameters is not None:
            nodes += [self.parameters]

        if self.return_type is not None:
            nodes += [self.return_type]

        return nodes

    def __init__(self, identifier, parameters, return_type):
        self.identifier = identifier
        self.parameters = parameters
        self.return_type = return_type

    @classmethod
    def construct(cls):
        if not cls.parser.next.has("fun"):
            return None

        cls.parser.take()
        identifier = cls.parser.expecting_of("Identifier")
        cls.parser.expecting_has("(")
        parameters = FunctionParameterList.construct()
        cls.parser.expecting_has(")")

        return cls(identifier, parameters, FunctionReturnType.construct())

    def transpile(self):
        return self.transpile_definition().finish(self)

    def transpile_definition(self, is_definition = False):
        if self.transpiler.context.in_block:
            self.transpiler.warnings.error(self, "Cannot declare function outside of global scope")

        if self.return_type is not None:
            return_type = self.return_type.transpile()
        else:
            return_type = Expression("", "void")

        function = self.transpiler.symbols.new_function(self, self.identifier.string)
        self.transpiler.context.function = function

        if is_definition:
            self.transpiler.push_symbol_table()
            function.symbols = self.transpiler.symbols

            if self.parameters is not None:
                self.parameters.is_def = True

        parameters = self.parameters.transpile() if self.parameters is not None else "void"
        statement = Statement(return_type)

        if not is_definition and function.declared:
            self.transpiler.warnings.error(self, "Cannot declare function twice")

        function.set_parameters(self, self.parameters)
        function.set_return_type(self, self.return_type)
        function.declared = True

        if is_definition:
            function.define()
        else:
            self.transpiler.context.function = None

        return statement.add(after = f" {function.c_name}({parameters})")

class FunctionParameterList(Node):
    @property
    def nodes(self) -> list:
        return self.parameters

    def __init__(self, parameters):
        self.parameters = parameters
        self.is_def = False

    @classmethod
    def construct(cls):
        positional = True
        parameters = []

        while cls.parser.next.has(*TYPE_KEYWORDS, *TYPE_MODIFIER_KEYWORDS):
            parameters += [FunctionParameter.construct()]

            if parameters[-1].default is None and not positional:
                message = "Positional parameter cannot follow default parameter"
                cls.parser.warnings.error(parameters[-1], message)

            positional = parameters[-1].default is None

            if cls.parser.next.has(","):
                cls.parser.take()

        return None if len(parameters) == 0 else cls(parameters)

    def transpile(self):
        first, *parameters = self.parameters
        expression = first.transpile_def() if self.is_def else first.transpile()

        for parameter in parameters:
            result = parameter.transpile_def() if self.is_def else parameter.transpile()
            expression.add(after = f", {result}")

        return expression

class FunctionParameter(Node):
    @property
    def nodes(self) -> list:
        nodes = [self.full_type]

        if self.borrow_qualifier is not None:
            nodes += [self.borrow_qualifier]

        if self.identifier is not None:
            nodes += [self.identifier]

        if self.default is not None:
            nodes += [self.default]

        return nodes

    def __init__(self, full_type, borrow_qualifier, identifier, default):
        self.full_type = full_type
        self.borrow_qualifier = borrow_qualifier
        self.identifier = identifier
        self.default = default
        self._qualifiers = None

    @classmethod
    def construct(cls):
        full_type = FullType.construct()
        borrow = cls.parser.take() if cls.parser.next.has("&", "$") else None
        identifier = cls.parser.take() if cls.parser.next.of("Identifier") else None
        default = None

        if cls.parser.next.has("="):
            if identifier is None:
                message = "Default parameter must be given identifier"
                cls.parser.warnings.error(cls.parser.take(), message)
            elif borrow is not None:
                message = "Default parameter cannot be borrow or ownership"
                cls.parser.warnings.error(cls.parser.take(), message)
                cls.parser.expression.construct()
            else:
                cls.parser.take()
                default = cls.parser.expression.construct()

        return cls(full_type, borrow, identifier, default)

    def transpile(self):
        expression = self.full_type.transpile()

        if self.borrow_qualifier is not None:
            expression.add(after = "*")

        if self.identifier is not None:
            expression.add(after = f" {self.identifier.string}")
            f_kind = self.transpile_qualifiers()

            if f_kind.defaults is not None:
                f_kind.defaults[1].verify_assign(self, expression)

        return expression

    def transpile_def(self):
        f_kind = self.transpile_qualifiers()
        name = self.identifier.string if self.identifier is not None else ""

        if f_kind.qualifier == "var":
            parameter = self.transpiler.symbols.new_variable(self, name, f_kind.kind)
        else:
            parameter = self.transpiler.symbols.new_invariable(self, name, f_kind.kind)

        if f_kind.defaults is not None:
            f_kind.defaults[1].verify_assign(self, Expression(parameter.kind))

        parameter.initialized = True
        parameter.arrays = f_kind.arrays
        parameter.ownership = f_kind.borrow
        parameter.heap = (f_kind.borrow == "$")

        kind = self.full_type.transpile()

        if parameter.ownership is not None:
            kind.add(after = "*")

        return Expression("", f"{kind} {parameter.c_name}")

    def transpile_qualifiers(self):
        if self._qualifiers is not None:
            return self._qualifiers

        qualifier = self.full_type.qualifier
        if qualifier is not None: qualifier = qualifier.string

        kind = self.full_type.keyword.token.string
        borrow = self.borrow_qualifier
        if borrow is not None: borrow = borrow.string

        arrays = self.full_type.arrays

        defaults = self.default
        if defaults is not None:
            defaults = self.default.transpile().assert_constant(self)
            defaults = (self.identifier.string, defaults)

        self._qualifiers = FunctionKind(qualifier, kind, arrays, borrow, defaults)
        return self._qualifiers

class FunctionReturnType(Node):
    @property
    def nodes(self) -> list:
        nodes = [self.full_type]

        if self.borrow is not None:
            nodes += [self.borrow]

        return nodes

    @property
    def components(self):
        components = [self.full_type.keyword.token.string]

        qualifier = self.full_type.qualifier

        if qualifier is not None:
            qualifier = qualifier.string

        components = [qualifier, *components]
        components += [self.full_type.arrays]
        components += [self.borrow.string] if self.borrow is not None else [None]

        return tuple(components)

    def __init__(self, full_type, borrow):
        self.full_type = full_type
        self.borrow = borrow

    @classmethod
    def construct(cls):
        if not cls.parser.next.has("->"):
            return None

        cls.parser.take().kind = "Punctuator"

        full_type = FullType.construct()
        borrow = cls.parser.take() if cls.parser.next.has("$") else None

        return cls(full_type, borrow)

    def transpile(self):
        statement = self.full_type.transpile()

        if self.borrow is not None:
            statement.add(after = "*")

        return statement
