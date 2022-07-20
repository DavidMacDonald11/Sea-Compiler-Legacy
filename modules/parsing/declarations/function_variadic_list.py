from ..node import Node

class FunctionVariadicList(Node):
    @classmethod
    def construct(cls, children):
        children.make("TypeName")

        if children.next_token.of("Identifier"):
            children.take()

        variadic = False

        while not variadic and children.next_token.has(","):
            children.take()
            children.make("TypeName")

            if children.next_token.has("*"):
                children.take()
                variadic = True

            if children.next_token.of("Identifier"):
                children.take()

        return cls(children)
