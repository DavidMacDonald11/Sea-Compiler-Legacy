from ..expressions.expression import Expression
from ..node import Node, PrimaryNode

class BlockableStatement(Node):
    @property
    def nodes(self) -> list:
        return [self.statement]

    def __init__(self, statement):
        self.statement = statement

    def tree_repr(self, prefix):
        return self.statement.tree_repr(prefix)

    @classmethod
    def construct(cls):
        statement = BlockableStatementComponent.construct()

        if statement is not None:
            cls.parser.expecting_has(r"\n", "EOF")
            return cls(statement)

        return None

    def transpile(self):
        statement = self.statement.transpile().new(f"{self.indent}%s;")

        if isinstance(self.statement, ReturnStatement):
            statement.new("%s/*%e*/")

        return statement

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
        return self.transpiler.expression("", "/*pass*/")

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
        statement = self.transpiler.expression()
        keyword = self.keyword.string

        if not self.transpiler.context.in_loop:
            self.transpiler.warnings.error(self, f"Cannot use {keyword} statement outside of loop")

        if self.label is None:
            return statement.new(keyword)

        label = self.transpiler.symbols.at(self, self.label.string)

        if label is None:
            return statement.new(f"/*{keyword} {self.label.string}*/")

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
        statement = self.transpiler.expression("", "return")

        if not self.transpiler.context.in_function:
            self.transpiler.warnings.error(self, "Cannot use return statement outside of function")
            return statement.new(f"/*%s {self.expression.transpile()}*/")

        function = self.transpiler.context.function
        func = function.return_expression(self)
        f_kind = self.expression_kind(func)

        return self.check_return_kinds(statement.cast(func.e_type), func, f_kind)

    def check_return_kinds(self, statement, func, f_kind):
        statement = self.check_missing_return(statement, func, f_kind)
        statement, expression = self.transpile_expression(statement, func)

        if func.e_type == "":
            self.transpiler.warnings.error(self, "Function should not return anything")
            return statement.new("/*%s*/")

        e_type = self.transpiler.expression.resolve(expression, func).e_type
        matches_ownership = expression.ownership == func.ownership
        matches_invar = not expression.is_invar or func.is_invar

        if e_type == func.e_type and matches_ownership and matches_invar:
            return statement

        e_kind = self.expression_kind(expression.cast(e_type))
        message = f"Function returns {f_kind}; found {e_kind}"
        self.transpiler.warnings.error(self, message)

        return statement.new("/*%s*/")

    def check_missing_return(self, statement, func, f_kind):
        if self.expression is not None or func.e_type == "":
            return statement

        self.transpiler.warnings.error(self, f"Function must return {f_kind}")
        return statement.new("/*%s*/")

    def transpile_expression(self, statement, func):
        self.transpiler.context.in_return = True
        expression = self.expression.transpile()

        if func.e_type not in ("c64", "cmax"):
            expression.drop_imaginary(self)

        self.transpiler.context.in_return = False

        statement.new(f"%s {expression}")
        return statement, expression

    def expression_kind(self, expression):
        e_qualifier = "invar" if expression.is_invar else "var"
        e_borrow = expression.ownership
        e_borrow = "ownership" if e_borrow == "$" else "borrow" if e_borrow == "&" else "value"

        return f"{e_qualifier} {expression.e_type} {e_borrow}"
