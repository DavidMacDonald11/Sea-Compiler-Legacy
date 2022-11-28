from .comparative_expression import ComparativeExpression
from ..declarations.type_keyword import TypeKeyword
from ..node import Node

class TypeCheckExpression(Node):
    @property
    def nodes(self) -> list:
        return [self.expression, *self.keywords, self.type_keyword]

    def __init__(self, expression, keywords, type_keyword):
        self.expression = expression
        self.keywords = keywords
        self.type_keyword = type_keyword

    @classmethod
    def construct(cls):
        expression = ComparativeExpression.construct()

        while cls.parser.next.has("is"):
            keywords = [cls.parser.take()]
            keywords = [*keywords, cls.parser.take()] if cls.parser.next.has("not") else keywords
            expression = cls(expression, keywords, TypeKeyword.construct())

        return expression

    def transpile(self):
        self.transpiler.context.type_checks += 1
        expression = self.expression.transpile().operate(self, check_any = False)
        negate = len(self.keywords) > 1
        type_keyword = self.type_keyword.transpile()
        self.transpiler.context.type_checks -= 1

        if self.type_keyword.token.string == "any":
            self.transpiler.warnings.error(self, "Cannot check if type is any")
            return expression.new("%s /*is (not) any*/")

        if expression.e_type != "any":
            e_type = self.transpiler.expression.resolve(expression, type_keyword).e_type
            result = e_type != type_keyword.e_type if negate else e_type == type_keyword.e_type
            return expression.new(f"{int(result)}").cast("bool")

        # TODO consider as parameters
        # TODO casting
        # TODO values must match exact type b/c of pointer

        if type_keyword.e_type == "str":
            op = "!=" if negate else "=="
        else:
            op = ">" if negate else "<="

        return expression.new(f"%s {op} {type_keyword.any_type}").cast("bool")
