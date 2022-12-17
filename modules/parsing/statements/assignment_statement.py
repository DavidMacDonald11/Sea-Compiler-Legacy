from transpiling.expression import OwnershipExpression
from transpiling.statement import Statement
from transpiling.utils import util, new_util
from ..expressions.expression import Expression
from ..expressions.primary_expression import Identifier
from ..node import Node

class AssignmentStatement(Node):
    @property
    def nodes(self) -> list:
        return self.expression_lists

    def __init__(self, expression_lists):
        self.expression_lists = expression_lists
        self.identifiers = []

    def __len__(self):
        return len(self.expression_lists)

    @classmethod
    def construct(cls):
        taken = cls.parser.take()

        if not cls.parser.next.has("=", ",") and not taken.has("["):
            cls.parser.i -= 1
            return cls([ExpressionList.construct()])

        cls.parser.i -= 1
        expression_lists = [ExpressionList.construct()]

        while cls.parser.next.has("="):
            cls.parser.take()
            expression_lists += [ExpressionList.construct()]

        return cls(expression_lists)

    def transpile(self):
        return AssignmentList.transpile_lists(self.make_lists())

    def make_lists(self, definition = None, declaration = None):
        identifier_lists, lists, kind = self.initalize_lists(declaration)

        for identifiers in identifier_lists:
            self.move_identifiers_into_lists(identifiers, lists, kind, definition)

        return lists

    def initalize_lists(self, declaration):
        identifier_lists = self.expression_lists[:-1]
        expressions = self.expression_lists[-1]

        if declaration is not None:
            identifier_lists = [ExpressionList(declaration.identifiers), *identifier_lists]
            kind = (declaration.type_keyword.token.string, declaration.arrays)

            for name in declaration.identifiers[::-1]:
                declaration.transpile_name(name.string, kind[0])
        else:
            kind = None

        for identifiers in identifier_lists:
            if len(identifiers) != len(expressions):
                raise self.transpiler.warnings.fail(self, "Mismatched number of values")

        lists = [AssignmentList([], x, self.identifiers) for x in expressions]
        return identifier_lists, lists, kind

    def move_identifiers_into_lists(self, identifiers, lists, kind, definition):
        for j, identifier in enumerate(identifiers):
            is_token = not isinstance(identifier, Node) and identifier.of("Identifier")

            if not identifier.of(Identifier) and not is_token:
                message = f"Cannot assign value to {type(identifier).__name__}"
                self.transpiler.warnings.error(self, message)

            lists[j] += identifier

            if kind is not None:
                lists[j].kind = kind
                lists[j].check = definition.check_references

class ExpressionList(Node):
    @property
    def nodes(self) -> list:
        return self.expressions

    def __init__(self, expressions):
        self.expressions = expressions

    def __len__(self):
        return len(self.expressions)

    def __getitem__(self, key):
        return self.expressions[key]

    @classmethod
    def construct(cls):
        expressions = [Expression.construct()]

        while cls.parser.next.has(","):
            cls.parser.take()
            expressions += [Expression.construct()]

        return cls(expressions)

    def transpile(self):
        raise NotImplementedError(type(self).__name__)

class AssignmentList(Node):
    @property
    def nodes(self) -> list:
        return [*self.identifiers, self.expression]

    def __init__(self, identifiers, expression, others, kind = None, check = None):
        self.identifiers = identifiers
        self.expression = expression
        self.others = others
        self.kind = kind
        self.check = check

    def __iadd__(self, other):
        self.identifiers += [other]
        return self

    @classmethod
    def construct(cls):
        raise NotImplementedError(cls.__name__)

    @classmethod
    def transpile_lists(cls, a_lists):
        statement = Statement()

        for a_list in a_lists:
            result = a_list.transpile().show_kind()
            statement.new_prefix(result.finish(a_list)).append()

        return statement

    def transpile(self):
        self.transpiler.context.in_assign = True
        statement = self.transpile_identifiers()
        self.transpiler.context.in_assign = False

        return statement

    def transpile_identifiers(self):
        result = None
        temped = len(self.others) == 0

        for i, identifier in enumerate(self.identifiers[::-1]):
            name = identifier.token.string
            identifier = self.transpiler.symbols.at(self, name)
            declaration = self.kind is not None and i == len(self.identifiers) - 1

            self.others += [name]

            if declaration:
                identifier.arrays = self.kind[1]

            if identifier.arrays > 0:
                self.transpiler.context.array = identifier
                statement = Statement(self.expression.transpile()).cast(identifier.kind)
                self.transpiler.context.array = None
            else:
                statement = Statement(self.expression.transpile())

            if not temped:
                temped = self.handle_temporaries(statement)

            is_own = isinstance(statement.expression, OwnershipExpression)

            access = identifier.c_access if identifier.ownership is not None else f"{identifier}"
            identifier.assign(self, statement.expression).add(f"{access} = ")
            self.check_declaration(statement, declaration, identifier, is_own)

            copyable = len(statement.expression.identifiers) > 0

            if (identifier.kind == "str" or identifier.arrays > 0) and copyable and not is_own:
                statement = self.copy_array(statement)

            if result is not None:
                result.append(statement).drop()
            else:
                result = statement

        return result or Statement()

    def handle_temporaries(self, statement):
        for identifier in self.others:
            if identifier in statement.expression.identifiers:
                self.transpiler.temps.new(statement)
                return True

        return False

    def check_declaration(self, statement, declaration, identifier, is_own):
        if declaration:
            if is_own:
                statement.expression.owners[1] = identifier
                statement.add("*")
                self.check(statement.expression)

            kind = "array" if self.kind[1] > 0 or self.kind[0] == "str" else self.kind[0]
            statement.add(f"__sea_type_{kind}__ ")
        elif is_own:
            message = "Must create new identifier to transfer ownership"
            self.transpiler.warnings.error(self, message)

    def copy_array(self, statement):
        if statement.expression.kind == "str":
            return self.transpiler.temps.copy_str(statement)

        # TODO copy arr
        return statement
