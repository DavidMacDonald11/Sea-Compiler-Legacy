from ..node import Node

class InitializerCompoundLiteral(Node):
    @classmethod
    def construct(cls, children):
        bracket = children.expecting_has("{", "[")
        cls.construct_initializer_list(children, bracket)
        children.expecting_has("]" if bracket.has("[") else "}")

        return cls(children)

    @classmethod
    def construct_initializer_list(cls, children, bracket):
        node = children.make("RangedGenerator")
        node = node or children.make("IterativeGenerator")

        if node is not None:
            return node

        children.ignore_format_tokens()
        children.make("DesignatedInitializer")

        while children.next_token.has(","):
            children.take()
            children.ignore_format_tokens()

            if children.next_token.has("]" if bracket.has("[") else "}"):
                return

            children.make("DesignatedInitializer")

        children.ignore_format_tokens()
