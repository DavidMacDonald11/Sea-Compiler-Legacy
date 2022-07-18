from ..node import Node

class TypeName(Node):
    @classmethod
    def construct(cls, children):
        cls.construct_reference(children)

        if not children.next_token.has("aligned"):
            return cls(children)

        children.take()
        children.expecting_has("to")

        nextt = children.next_token
        if nextt.of("Keyword") and not nextt.has("not") or nextt.has("+"):
            children.make("TypeName")
        else:
            children.make("ConstantExpression")

        return cls(children)

    @classmethod
    def construct_reference(cls, children):
        children.make("NonReferenceTypeName")
        qualfier = children.make("TypeQualifier")

        if children.next_token.has("@"):
            children.take().kind = "Punctuator"
            return cls(children)

        if qualfier is not None:
            qualfier.mark()
            children.warn("Incorrect type qualifier")

        return cls(children)

