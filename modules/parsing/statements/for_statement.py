from transpiling.expression import Expression
from transpiling.statement import Statement
from .block_statement import BlockStatement
from ..declarations.full_type import FullType
from ..expressions.postfix_access_expression import PostfixAccessExpression
from ..node import Node

class ForStatement(Node):
    @property
    def nodes(self) -> list:
        nodes = [self.full_type]

        if self.label is not None:
            nodes = [self.label, *nodes]

        if self.borrow is not None:
            nodes += [self.borrow]

        nodes += [self.identifier, self.expression, self.block]
        return nodes

    def __init__(self, label, full_type, borrow, identifier, expression, block):
        self.label = label
        self.full_type = full_type
        self.borrow = borrow
        self.identifier = identifier
        self.expression = expression
        self.block = block

    @classmethod
    def construct(cls):
        if cls.parser.next.has("for"):
            label = None
        elif cls.parser.next.of("Identifier"):
            label = cls.parser.take()

            if not cls.parser.next.has("for"):
                cls.parser.i -= 1
                return None
        else:
            return None

        cls.parser.take()

        full_type = FullType.construct()
        borrow = cls.parser.take() if cls.parser.next.has("$", "&") else None
        identifier = cls.parser.expecting_of("Identifier")

        cls.parser.expecting_has("in")
        expression = cls.parser.expression.construct()
        cls.parser.expecting_has(":")
        block = BlockStatement.construct()

        return cls(label, full_type, borrow, identifier, expression, block)

    def transpile(self):
        self.transpiler.context.loops += 1
        self.transpiler.push_symbol_table()

        declaration = self.full_type.transpile()
        expression = self.expression.transpile()

        if expression.kind != "str" and expression.arrays < 1:
            self.transpiler.warnings.error(self, "Cannot iterate over non-array")

        declaration.verify_index(self, expression)

        if self.borrow is not None:
            declaration.add(after = "*")
            raise NotImplementedError("Cannot take ownership of index of array (yet)")

        name = self.identifier.string

        qualifier = self.full_type.qualifier
        if qualifier is not None: qualifier = qualifier.string

        if qualifier != "invar":
            identifier = self.transpiler.symbols.new_variable(self, name, declaration.kind)
        else:
            identifier = self.transpiler.symbols.new_invariable(self, name, declaration.kind)

        identifier.ownership = self.borrow
        identifier.arrays = declaration.arrays
        identifier.initialized = True
        name = identifier.c_name

        i = self.transpiler.cache_new_temp(Expression("nat", "0"))
        self.transpiler.cache_new_temp(expression)

        if expression.kind == "str" and expression.arrays == 0:
            index = PostfixAccessExpression.write_str_index_func(self.transpiler)
            kind = "char"
            access = f"{index}({expression}, {i})"
        else:
            index = PostfixAccessExpression.write_array_index_func(self.transpiler)
            kind = "array" if expression.kind == "str" or expression.arrays > 1 else expression.kind
            access = f"{index}(__sea_type_{kind}__, {expression}, {i})"

        condition = f"{i} < {expression}.size"
        reassign = f"{i}++, {name} = {access}"

        statement = Statement().finish(self).drop().append(Statement())
        statement.new(f"for({declaration} {name} = {access};")
        statement.append(Statement().new(condition).finish(self))
        statement.new_append(Statement().new(f"{reassign})"))

        if self.label is not None:
            label = self.transpiler.symbols.new_label(self, self.label.string)

        statement.new_append(self.block.transpile_without_symbol_table()).drop()

        if self.label is not None:
            label.surround(statement)

        self.transpiler.context.loops -= 1
        return statement.finish(self, semicolons = False)
