from .expression_statement import ExpressionStatement
from ..expressions.expression import Expression
from ..expressions.primary_expression import Identifier
from ..node import Node

class AssignmentStatement(Node):
    @property
    def nodes(self) -> list:
        return self.expression_lists

    def __init__(self, expression_lists):
        self.expression_lists = expression_lists

    @classmethod
    def construct(cls):
        cls.parser.take()

        if not cls.parser.next.has("=", ","):
            cls.parser.i -= 1
            return ExpressionStatement.construct()

        cls.parser.i -= 1
        expression_lists = [ExpressionList.construct()]

        while cls.parser.next.has("="):
            cls.parser.take()
            expression_lists += [ExpressionList.construct()]

        cls.parser.expecting_has(r"\n", "EOF")

        return cls(expression_lists)

    def transpile(self):
        statement = None

        for pair in self.create_pairs():
            result = pair.transpile()
            statement = result if statement is None else statement.new(f"%s;\n{result}")

        return statement

    def create_pairs(self, declaration = None):
        pairs = []
        gen = None

        identifier_lists = self.expression_lists[:-1]
        expressions = self.expression_lists[-1]

        if declaration is not None:
            identifier_lists = [ExpressionList(declaration.identifiers), *identifier_lists]
            gen = declaration.transpile_generator()

        self.verify_expressions(identifier_lists, expressions, pairs, gen)

        return pairs

    def verify_expressions(self, identifier_lists, expressions, pairs, gen):
        mismatched = False

        for expression in expressions:
            if expression.transpile().ownership is not None:
                message = "Cannot transfer ownership to multiple identifiers"
                self.transpiler.warnings.error(self, message)

        for identifiers in identifier_lists:
            if not mismatched and len(identifiers) != len(expressions):
                self.transpiler.warnings.error(self, "Mismatched number of values")
                mismatched = True

            self.verify_identifiers(identifiers, expressions, pairs, gen)

    def verify_identifiers(self, identifiers, expressions, pairs, gen):
        for i, identifier in enumerate(identifiers.expressions):
            is_token = not isinstance(identifier, Node) and identifier.of("Identifier")

            if not identifier.of(Identifier) and not is_token:
                message = f"Cannot assign value to {type(identifier).__name__}"
                self.transpiler.warnings.error(self, message)

            self.transpiler.warnings.check()

            try:
                decl_info = next(gen)[0]
            except (StopIteration, TypeError):
                decl_info = gen = None

            pairs += [AssignmentPair(identifier, expressions[i], decl_info)]

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

class AssignmentPair(Node):
    @property
    def nodes(self) -> list:
        return [self.identifier, self.expression]

    def __init__(self, identifier, expression, decl_info = None):
        self.identifier = identifier
        self.expression = expression
        self.decl_info = decl_info

    @classmethod
    def construct(cls):
        raise NotImplementedError(cls.__name__)

    def transpile(self):
        name = self.identifier.token.string
        identifier = self.transpiler.symbols.at(self, name)
        expression = self.expression.transpile()

        if identifier is None:
            return expression.new(f"/*{name} = */%s")

        expression = identifier.assign(self, expression).new(f"{identifier} = %s")

        if self.decl_info is not None:
            expression = expression.new(f"{self.decl_info} %s")

        return expression
