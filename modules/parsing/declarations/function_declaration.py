from transpiling.statement import Statement
from transpiling.expression import Expression
from transpiling.symbols.function import FunctionKind
from lexing.token import TYPE_KEYWORDS, TYPE_MODIFIER_KEYWORDS
from .type_keyword import TypeKeyword
from ..node import Node

# TODO verify returns from all branches
# TODO add varargs

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
        nodes = [self.type_keyword]

        if self.type_qualifier is not None:
            nodes = [self.type_qualifier, *nodes]

        if self.borrow_qualifier is not None:
            nodes += [self.borrow_qualifier]

        if self.identifier is not None:
            nodes += [self.identifier]

        if self.default is not None:
            nodes += [self.default]

        return nodes

    def __init__(self, type_qualifier, type_keyword, borrow_qualifier, identifier, default):
        self.type_qualifier = type_qualifier
        self.type_keyword = type_keyword
        self.borrow_qualifier = borrow_qualifier
        self.identifier = identifier
        self.default = default
        self._qualifiers = None

    @classmethod
    def construct(cls):
        type_qualifier = cls.parser.take() if cls.parser.next.has(*TYPE_MODIFIER_KEYWORDS) else None
        type_keyword = TypeKeyword.construct()
        borrow_qualifier = cls.parser.take() if cls.parser.next.has("&", "$") else None
        identifier = cls.parser.take() if cls.parser.next.of("Identifier") else None
        default = None

        if cls.parser.next.has("="):
            if identifier is None:
                message = "Default parameter must be given identifier"
                cls.parser.warnings.error(cls.parser.take(), message)
            elif borrow_qualifier is not None:
                message = "Default parameter cannot be borrow or ownership"
                cls.parser.warnings.error(cls.parser.take(), message)
                cls.parser.expression.construct()
            else:
                cls.parser.take()
                default = cls.parser.expression.construct()

        return cls(type_qualifier, type_keyword, borrow_qualifier, identifier, default)

    def transpile(self):
        expression = self.type_keyword.transpile()

        if self.borrow_qualifier is not None:
            expression.add(after = "*")

        if self.identifier is not None:
            expression.add(after = f" {self.identifier.string}")

        return expression

    def transpile_def(self):
        f_kind = self.transpile_qualifiers()
        name = self.identifier.string if self.identifier is not None else ""

        if f_kind.qualifier == "var":
            parameter = self.transpiler.symbols.new_variable(self, name, f_kind.kind)
        else:
            parameter = self.transpiler.symbols.new_invariable(self, name, f_kind.kind)

        if f_kind.defaults is not None:
            parameter.assign(self, f_kind.defaults[1])

        parameter.initialized = True
        parameter.ownership = f_kind.borrow
        keyword = self.type_keyword.transpile()

        if parameter.ownership is not None:
            keyword.add(after = "*")

        return Expression("", f"{keyword} {parameter.c_name}")

    def transpile_qualifiers(self):
        if self._qualifiers is not None:
            return self._qualifiers

        qualifier = self.type_qualifier
        if qualifier is not None: qualifier = qualifier.string

        kind = self.type_keyword.token.string
        borrow = self.borrow_qualifier
        if borrow is not None: borrow = borrow.string

        defaults = self.default
        if defaults is not None:
            defaults = self.default.transpile().assert_constant(self)
            defaults = (self.identifier.string, defaults)

        self._qualifiers = FunctionKind(qualifier, kind, borrow, defaults)
        return self._qualifiers

class FunctionReturnType(Node):
    @property
    def nodes(self) -> list:
        nodes = [self.keyword]

        if self.qualifier is not None:
            nodes = [self.qualifier, *nodes]

        if self.borrow is not None:
            nodes += [self.borrow]

        return nodes

    @property
    def components(self):
        components = [self.keyword.token.string]
        components = [self.qualifier.string if self.qualifier is not None else None, *components]
        components += [self.borrow.string] if self.borrow is not None else [None]

        return tuple(components)

    def __init__(self, qualifier, keyword, borrow):
        self.qualifier = qualifier
        self.keyword = keyword
        self.borrow = borrow

    @classmethod
    def construct(cls):
        if not cls.parser.next.has("->"):
            return None

        cls.parser.take().kind = "Punctuator"

        qualifier = cls.parser.take() if cls.parser.next.has(*TYPE_MODIFIER_KEYWORDS) else None
        keyword = TypeKeyword.construct()
        borrow = cls.parser.take() if cls.parser.next.has("$") else None

        return cls(qualifier, keyword, borrow)

    def transpile(self):
        statement = self.keyword.transpile()

        if self.borrow is not None:
            statement.add(after = "*")

        return statement
