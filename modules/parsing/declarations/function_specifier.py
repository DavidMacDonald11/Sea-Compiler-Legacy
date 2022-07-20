from ..node import Node

class FunctionSpecifier(Node):
    @classmethod
    def construct(cls, children):
        children.make("StorageClassSpecifier")

        if children.next_token.has("inline"):
            children.take()

            if children.next_token.has("deviant"):
                children.take()

            return cls(children)

        if children.next_token.has("deviant"):
            children.take()

        if children.next_token.has("inline"):
            children.take()

        return None if len(children.nodes) == 0 else cls(children)
