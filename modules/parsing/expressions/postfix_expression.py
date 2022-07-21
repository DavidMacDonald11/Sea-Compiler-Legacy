from ..node import Node

class PostfixExpression(Node):
    def construct(self, parser):
        def recursive_construct(parser, head):
            parser = parser.new()
            parser.children += head

            node = parser.make("SliceOperator")
            node = node or parser.make("CallOperator")
            node = node or self.construct_access(parser)
            node = node or self.construct_unary(parser)

            if node is None:
                return head

            return recursive_construct(parser, node)

        return recursive_construct(parser, parser.make("PrimaryExpression"))

    def construct_access(self, parser):
        if not parser.next.has(".", "->"):
            return None

        parser.take()
        parser.expecting_of("Identifier")

        self.specifier = "Access"
        return self

    def construct_unary(self, parser):
        if not parser.next.has("++", "--", "%", "!"):
            return None

        parser.take()

        self.specifier = "Unary"
        return self
