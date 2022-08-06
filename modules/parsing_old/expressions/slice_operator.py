from ..node import Node

class SliceOperator(Node):
    def construct(self, parser):
        if not parser.next.has("["):
            return None

        parser.take()

        if parser.next.has("]"):
            parser.take_and_warn("Cannot have empty array index")
            return self

        if not parser.next.has(":", "]"):
            parser.make("AssignmentExpression")

        if parser.next.has(":"):
            parser.take()

        if not parser.next.has(":", "]"):
            parser.make("AssignmentExpression")

        if parser.next.has(":"):
            parser.take()

        if not parser.next.has(":", "]"):
            parser.make("AssignmentExpression")

        parser.expecting_has("]")
        return self
