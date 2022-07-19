from ..node import Node

class ElementDeclaration(Node):
    @classmethod
    def construct(cls, children):
        children.make("TypeName")
        children.expecting_of("Identifier")

        while children.next_token.has(","):
            children.take()

            if children.next_token.of("Identifier"):
                children.take()

                if children.next_token.of("Identifier"):
                    children.take()
            else:
                children.make("TypeName")
                children.expecting_of("Identifier")

        return cls(children)
