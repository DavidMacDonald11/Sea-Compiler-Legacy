from lexing.token import TYPE_KEYWORDS, TYPE_MODIFIER_KEYWORDS
from .type_keyword import TypeKeyword
from ..node import Node

# TODO verify return types
# TODO allow ownership return value/type
# TODO consider functions in blocks
# TODO imag args should drop j suffix
# TODO create contexts to solve above

# TODO implement function overloading
# TODO improve mismatching type error
# TODO verify called function is defined eventually

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

        if cls.parser.next.has("->"):
            cls.parser.take().kind = "Punctuator"
            return_type = TypeKeyword.construct()
        else:
            return_type = None

        return cls(identifier, parameters, return_type)

    def transpile(self):
        return self.transpile_definition()

    def transpile_definition(self, is_definition = False):
        return_type = self.return_type.transpile() if self.return_type is not None else "void"
        function = self.transpiler.symbols.new_function(self, return_type, self.identifier.string)

        if is_definition:
            self.transpiler.push_symbol_table()

            if self.parameters is not None:
                self.parameters.is_def = True

        parameters = self.parameters.transpile() if self.parameters is not None else "void"
        statement = self.transpiler.expression("", f"{return_type}")

        if function is None:
            return statement.new(f"/*%s {self.identifier.string}({parameters})*/")

        if not is_definition and function.declared:
            self.transpiler.warnings.error(self, "Cannot declare function twice")

        function.set_parameters(self, self.parameters)
        function.set_return_type(self, self.return_type)
        function.declared = True

        if is_definition:
            function.define()

        return statement.new(f"%s {function.c_name}({parameters});")

class FunctionParameterList(Node):
    @property
    def nodes(self) -> list:
        return self.parameters

    def __init__(self, parameters):
        self.parameters = parameters
        self.is_def = False

    @classmethod
    def construct(cls):
        parameters = []

        while cls.parser.next.has(*TYPE_KEYWORDS, *TYPE_MODIFIER_KEYWORDS):
            parameters += [FunctionParameter.construct()]

            if cls.parser.next.has(","):
                cls.parser.take()

        return None if len(parameters) == 0 else cls(parameters)

    def transpile(self):
        first, *parameters = self.parameters
        statement = first.transpile_def() if self.is_def else first.transpile()

        for parameter in parameters:
            result = parameter.transpile_def() if self.is_def else parameter.transpile()
            statement = statement.new(f"%s, {result}")

        return statement

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

        return nodes

    def __init__(self, type_qualifier, type_keyword, borrow_qualifier, identifier):
        self.type_qualifier = type_qualifier
        self.type_keyword = type_keyword
        self.borrow_qualifier = borrow_qualifier
        self.identifier = identifier

    @classmethod
    def construct(cls):
        type_qualifier = cls.parser.take() if cls.parser.next.has(*TYPE_MODIFIER_KEYWORDS) else None
        type_keyword = TypeKeyword.construct()
        borrow_qualifier = cls.parser.take() if cls.parser.next.has("&", "$") else None
        identifier = cls.parser.take() if cls.parser.next.of("Identifier") else None

        return cls(type_qualifier, type_keyword, borrow_qualifier, identifier)

    def transpile(self):
        statement = self.type_keyword.transpile()

        if self.borrow_qualifier is not None:
            statement = statement.new("%s*")

        if self.identifier is not None:
            statement = statement.new(f"%s {self.identifier.string}")

        return statement

    def transpile_def(self):
        qualifier, keyword, borrow = self.transpile_qualifiers()
        name = self.identifier.string if self.identifier is not None else ""

        if qualifier == "var":
            parameter = self.transpiler.symbols.new_variable(self, keyword, name)
        else:
            parameter = self.transpiler.symbols.new_invariable(self, keyword, name)

        if parameter is None:
            return self.transpiler.expression("", f"/*{keyword} {name}*/")

        parameter.initialized = True
        parameter.ownership = borrow
        keyword = self.type_keyword.transpile()

        if parameter.ownership is not None:
            keyword = keyword.new("%s*")

        return self.transpiler.expression("", f"{keyword} {parameter.c_name}")

    def transpile_qualifiers(self):
        qualifier = self.type_qualifier
        borrow = self.borrow_qualifier

        has_qualifier = qualifier is not None
        has_borrow = borrow is not None

        if not has_borrow and not has_qualifier or has_qualifier and qualifier.string == "var":
            qualifier = "var"
        else:
            qualifier = "invar"

        borrow = borrow.string if has_borrow else None
        keyword = self.type_keyword.token.string

        return qualifier, keyword, borrow
