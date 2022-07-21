from ..node import Node

class TypeName(Node):
    def construct(self, parser):
        self.construct_reference(parser)

        if not parser.next.has("aligned"):
            return self

        parser.take()
        parser.expecting_has("to")
        parser.make("TypeName" if parser.next.may_be_type() else "ConstantExpression")

        return self

    def construct_reference(self, parser):
        parser.make("NonReferenceTypeName")
        qualifier = parser.make("TypeQualifier")

        if parser.next.has("@"):
            parser.take().kind = "Punctuator"
            return self

        if qualifier is not None:
            qualifier.mark()
            parser.warn("Incorrect type qualifier")

        return self

