from ..node import Node

class NonReferenceTypeName(Node):
    def construct(self, parser):
        def recursive_construct(parser, head):
            parser = parser.new()
            parser.children += head

            qualifier = parser.make("TypeQualifier")

            node = self.construct_array(parser)
            node = node or self.construct_pointer(parser)

            if node is not None:
                return recursive_construct(parser, node)

            if qualifier is None:
                return head

            head.children += qualifier
            qualifier.mark()
            head.parser.warn("Incorrect type qualifier")

            return head

        qualifier = parser.make("SpecifiersAndQualifiers")
        node = parser.make("TypeSpecifier")
        node.children += qualifier

        return recursive_construct(parser, node)

    def construct_array(self, parser):
        if not parser.next.has("["):
            return None

        parser.take()

        if parser.next.has("*"):
            parser.ignore()

            if parser.next.has("]"):
                parser.take_previous().kind = "Punctuator"
                parser.take()
                return self

            parser.unignore()

        if parser.next.has(">="):
            parser.take().kind = "Punctuator"

        parser.make("AssignmentExpression")
        parser.expecting_has("]")

        return self

    def construct_pointer(self, parser):
        if not parser.next.has("^"):
            return None

        parser.take().kind = "Punctuator"
        return self
