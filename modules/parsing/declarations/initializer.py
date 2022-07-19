from ..node import Node

class Initializer(Node):
    @classmethod
    def construct(cls, children):
        return cls.full_construct(children, "AssignmentExpression")

    @classmethod
    def full_construct(cls, children, expression_kind):
        if children.next_token.has("alloc"):
            children.take()

            if children.next_token.has("as"):
                children.take()
                children.make("Initializer")

            return cls(children)

        if children.next_token.has("realloc"):
            children.take()
            children.make("Expression")

            if children.next_token.has("to"):
                children.take()
                children.make("Initializer")

            if children.next_token.has("as"):
                children.take()
                children.make("Initializer")

            return cls(children)

        is_expression = not children.next_token.has("[", "{")
        kind = expression_kind if is_expression else "InitializerCompoundLiteral"
        children.make(kind)

        return cls(children)
