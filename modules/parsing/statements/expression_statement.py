from transpiling.expression import OwnershipExpression
from transpiling.statement import Statement
from ..expressions.expression import Expression
from .hidden_statement import HiddenStatement

class ExpressionStatement(HiddenStatement):
    @property
    def expression(self):
        return self.statement

    @classmethod
    def construct(cls):
        expression = Expression.construct()
        return cls(expression)

    def transpile(self):
        if isinstance(self.expression, OwnershipExpression):
            message = "Must assign result of ownership expression to an identifier"
            self.transpiler.warnings.error(self, message)

        return Statement(self.expression.transpile()).show_kind().finish(self)
