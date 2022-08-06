from ..node import Node

class PostfixExpression(Node):
    def construct(self, parser):
        def recursive_construct(parser, head):
            parser = self.parser.new()
            parser.children += head

            node = parser.make("SliceOperator")
            node = node or parser.make("CallOperator")
            node = node or PostfixExpression(parser).construct_access(parser)
            node = node or PostfixExpression(parser).construct_unary(parser)

            if node is None:
                return head

            return recursive_construct(parser, type(self)(parser))

        return recursive_construct(parser, parser.make("PrimaryExpression"))

    def construct_access(self, parser):
        if not parser.next.has(".", "->"):
            return None

        parser.take()
        parser.expecting_of("Identifier")

        self.specifier = "Access"
        return self

    def construct_unary(self, parser):
        if not parser.next.has("++", "--", "%", "!", "is"):
            return None

        parser.take()

        self.specifier = "Unary"
        return self
