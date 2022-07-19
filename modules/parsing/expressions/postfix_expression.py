from ..node import Node

class PostfixExpression(Node):
    @classmethod
    def construct(cls, children):
        def recursive_construct(children, head):
            children = children.next()
            children += head

            node = cls.construct_slice(children)
            node = node or cls.construct_call(children)
            node = node or cls.construct_access(children)
            node = node or cls.construct_unary(children)

            if node is None:
                return head

            return recursive_construct(children, node or head)

        return recursive_construct(children, children.make("PrimaryExpression"))

    @classmethod
    def construct_slice(cls, children):
        if not children.next_token.has("["):
            return None

        children.take()

        if children.next_token.has("]"):
            children.take_and_warn("Cannot have empty index or slice")
            return cls(children, "slice")

        if not children.next_token.has(":", "]"):
            children.make("AssignmentExpression")

        if children.next_token.has(":"):
            children.take()

        if not children.next_token.has(":", "]"):
            children.make("AssignmentExpression")

        if children.next_token.has(":"):
            children.take()

        if not children.next_token.has(":", "]"):
            children.make("AssignmentExpression")

        children.expecting_has("]")
        return cls(children, "slice")

    @classmethod
    def construct_call(cls, children):
        if not children.next_token.has("("):
            return None

        children.take()

        if children.next_token.has(")"):
            children.take()
            return cls(children, "call")

        children.make("AssignmentExpression")

        while children.next_token.has(","):
            children.take()

            if children.next_token.has(")"):
                children.take_and_warn("Expecting assignment-expression")
                return cls(children, "call")

            children.make("AssignmentExpression")

        children.expecting_has(")")
        return cls(children, "call")

    @classmethod
    def construct_access(cls, children):
        if not children.next_token.has(".", "->"):
            return None

        children.take()
        children.expecting_of("Identifier")
        return cls(children, "access")

    @classmethod
    def construct_unary(cls, children):
        if not children.next_token.has("++", "--", "%", "!"):
            return None

        children.take()
        return cls(children, "unary")
