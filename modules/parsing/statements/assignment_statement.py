from transpiling.expression import OwnershipExpression
from transpiling.statement import Statement
from .expression_statement import ExpressionStatement
from ..expressions.expression import Expression
from ..expressions.primary_expression import Identifier
from ..expressions.primary_expression import ExpressionList as PExpressionList
from ..node import Node

class AssignmentStatement(Node):
    @property
    def nodes(self) -> list:
        return self.expression_lists

    def __init__(self, expression_lists):
        self.expression_lists = expression_lists
        self.identifiers = []

    @classmethod
    def construct(cls):
        taken = cls.parser.take()

        if not cls.parser.next.has("=", ",") and not taken.has("["):
            cls.parser.i -= 1
            expression = Expression.construct()

            return cls([ExpressionList([expression])])

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
            kind = declaration.type_keyword.token.string

            for name in declaration.identifiers[::-1]:
                declaration.transpile_name(name.string, kind)
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
        self.was_primary = len(expressions) == 1 and isinstance(expressions[0], PExpressionList)
        self.expressions = expressions[0].expressions if self.was_primary else expressions

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

    def to_expression_statement(self):
        if self.was_primary:
            return ExpressionStatement(PExpressionList(self.expressions[0]))

        return ExpressionStatement(self.expressions[0])

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
        count = len(self.identifiers)
        expression = self.expression.transpile()

        if isinstance(expression, OwnershipExpression):
            if count > 1:
                message = "Cannot transfer ownership to multiple identifiers"
                self.transpiler.warnings.warn(self, message)
            elif count == 1 and self.kind is None:
                message = "Must create new identifier to transfer ownership"
                self.transpiler.warnings.warn(self, message)

        return self.transpile_identifiers(expression)

    def transpile_identifiers(self, expression):
        statement = Statement(expression)
        temped = len(self.others) == 0

        for i, identifier in enumerate(self.identifiers[::-1]):
            name = identifier.token.string
            identifier = self.transpiler.symbols.at(self, name)

            self.others += [name]

            if not temped:
                temped, expression = self.handle_temporaries(statement)

            access = identifier.c_access if identifier.ownership is not None else f"{identifier}"
            identifier.assign(self, statement.expression).add(f"{access} = ")

            if self.kind is not None and i == len(self.identifiers) - 1:
                if isinstance(statement.expression, OwnershipExpression):
                    statement.expression.owners[1] = identifier
                    statement.add("*")
                    self.check(statement.expression)

                statement.add(f"__sea_type_{self.kind}__ ")

        return statement

    def handle_temporaries(self, statement):  # sourcery skip: use-next
        for identifier in self.others:
            if identifier in statement.expression.identifiers:
                return True, self.transpiler.new_temp(statement)

        return False, statement
