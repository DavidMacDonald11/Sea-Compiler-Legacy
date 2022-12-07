from transpiling.statement import Statement
from transpiling.expression import Expression as TExpression, OwnershipExpression
from .hidden_statement import HiddenStatement
from ..expressions.expression import Expression
from ..node import Node, PrimaryNode

class BlockableStatement(HiddenStatement):
    @classmethod
    def construct(cls):
        statement = BlockableStatementComponent.construct()

        if statement is not None:
            cls.parser.expecting_has(r"\n", "EOF")
            return cls(statement)

        return None

    def transpile(self):
        return self.statement.transpile().finish(self)

class BlockableStatementComponent(Node):
    @classmethod
    def construct(cls):
        statement = PassStatement.construct() or BreakContinueStatement.construct()
        return statement or ReturnStatement.construct()

class PassStatement(PrimaryNode):
    @classmethod
    def construct(cls):
        return cls(cls.parser.take()) if cls.parser.next.has("pass") else None

    def transpile(self):
        return Statement().new("/*pass*/")

class BreakContinueStatement(Node):
    @property
    def nodes(self) -> list:
        return [self.keyword] if self.label is None else [self.keyword, self.label]

    def __init__(self, keyword, label):
        self.keyword = keyword
        self.label = label

    @classmethod
    def construct(cls):
        if not cls.parser.next.has("break", "continue"):
            return None

        keyword = cls.parser.take()
        label = cls.parser.take() if cls.parser.next.of("Identifier") else None

        return cls(keyword, label)

    def transpile(self):
        statement = Statement()
        keyword = self.keyword.string

        if not self.transpiler.context.in_loop:
            message = f"Cannot use '{keyword}' statement outside of loop"
            self.transpiler.warnings.error(self, message)

        if self.label is None:
            return statement.new(keyword)

        label = self.transpiler.symbols.at(self, self.label.string)
        return statement.new(f"goto {label.c_name}_{keyword}__")

class ReturnStatement(Node):
    @property
    def nodes(self) -> list:
        return [self.keyword] if self.expression is None else [self.keyword, self.expression]

    def __init__(self, keyword, expression):
        self.keyword = keyword
        self.expression = expression

    @classmethod
    def construct(cls):
        if not cls.parser.next.has("return"):
            return None

        keyword = cls.parser.take()

        if cls.parser.next.has(r"\n", "EOF"):
            return cls(keyword, None)

        return cls(keyword, Expression.construct())

    def transpile(self):
        statement = Statement().new("return")

        if not self.transpiler.context.in_function:
            self.transpiler.warnings.error(self, "Cannot use return statement outside of function")
            return statement

        function = self.transpiler.context.function
        func = function.return_expression()
        f_kind = self.expression_kind(func)

        statement = self.check_return_kinds(statement.cast(func.kind), func, f_kind)
        return statement.show_kind()

    def check_return_kinds(self, statement, func, f_kind):
        if self.expression is None:
            if func.kind != "":
                self.transpiler.warnings.error(self, f"Function must return {f_kind}")

            return statement

        statement, expression = self.transpile_expression(statement, func)

        if func.kind == "":
            self.transpiler.warnings.error(self, "Function should not return anything")
            return statement

        kind = TExpression.resolve(expression, func, True, True).kind
        e_owner = isinstance(expression, OwnershipExpression)
        f_owner = isinstance(func, OwnershipExpression)

        if e_owner and expression.owners[0] is not None and expression.owners[0].fun_local:
            self.transpiler.warnings.error(self, "Cannot return local identifier from function")

        if e_owner and f_owner:
            same = expression.operator == func.operator
            same = same and not expression.invariable or func.invariable
        else:
            same = (e_owner == f_owner)

        same = same and expression.arrays == func.arrays

        if kind == func.kind and same:
            return statement

        kind = self.expression_kind(expression.cast(kind))
        message = f"Function returns {f_kind}; found {kind}"
        self.transpiler.warnings.error(self, message)

        return statement

    def transpile_expression(self, statement, func):
        self.transpiler.context.in_return = True
        expression = self.expression.transpile()

        if "cplex" not in func.kind:
            expression.drop_imaginary(self)

        self.transpiler.context.in_return = False

        for line in Statement().lines[:-1]:
            statement.prefix(line)

        statement.add(after = f" {expression}")
        return statement, expression

    def expression_kind(self, expression):
        e_dims = "" if expression.arrays == 0 else f"{expression.arrays}D"

        if not isinstance(expression, OwnershipExpression):
            return f"var {e_dims} {expression.kind} value"

        e_qualifier = "invar" if expression.invariable else "var"
        e_borrow = expression.operator
        e_borrow = "ownership" if e_borrow == "$" else "borrow" if e_borrow == "&" else "value"

        return f"{e_qualifier} {e_dims} {expression.kind} {e_borrow}"
