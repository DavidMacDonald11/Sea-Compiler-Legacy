from ..node import Node

class Initializer(Node):
    expression_kind = "AssignmentExpression"

    def construct(self, parser):
        if parser.next.has("alloc"):
            parser.take()

            if parser.next.has("as"):
                parser.take()
                parser.make("Initializer")

            return self

        if parser.next.has("realloc"):
            parser.take()
            parser.make("Expression")

            if parser.next.has("to"):
                parser.take()
                parser.make("Initializer")

            return self

        is_expression = not parser.next.has("[", "{")
        kind = type(self).expression_kind if is_expression else "InitializerCompoundLiteral"
        parser.make(kind)

        return self
