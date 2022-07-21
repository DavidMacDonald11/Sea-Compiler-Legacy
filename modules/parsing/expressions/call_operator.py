from ..node import Node

class CallOperator(Node):
    def construct(self, parser):
        if not parser.next.has("("):
            return None

        parser.take()

        if parser.next.has(")"):
            parser.take()
            return self

        parser.make("AssignmentExpression")

        while parser.next.has(","):
            parser.take()

            if parser.next.has(")"):
                parser.take_and_warn("Expecting AssignmentExpression")
                return self

            parser.make("AssignmentExpression")

        parser.expecting_has(")")
        return self
