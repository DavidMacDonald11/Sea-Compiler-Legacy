from ..node import Node

class NonReferenceTypeName(Node):
    @classmethod
    def construct(cls, children):
        def recursive_construct(children, head):
            children = children.next()
            children += head

            qualifier = children.make("TypeQualifier")

            node = cls.construct_array(children)
            node = node or cls.construct_pointer(children)

            if node is None:
                if qualifier is not None:
                    head.children += qualifier
                    qualifier.mark()
                    head.children.warn("Incorrect type qualifier")

                return head

            return recursive_construct(children, node or head)

        qualifier = children.make("SpecifiersAndQualifiers")
        node = children.make("TypeSpecifier")

        node.children += qualifier

        return recursive_construct(children, node)

    @classmethod
    def construct_array(cls, children):
        if not children.next_token.has("["):
            return None

        children.take()

        if children.next_token.has("*"):
            children.ignore()

            if children.next_token.has("]"):
                children.take_previous().kind = "Punctuator"
                children.take()
                return cls(children)

            children.unignore()

        if children.next_token.has(">="):
            children.take().kind = "Punctuator"

        children.make("AssignmentExpression")
        children.expecting_has("]")

        return cls(children)

    @classmethod
    def construct_pointer(cls, children):
        if not children.next_token.has("^"):
            return None

        children.take().kind = "Punctuator"
        return cls(children)
