from ..node import Node
from ..node_children import NodeChildren

class Statement(Node):
    @classmethod
    def construct(cls, children):
        children.ignore_format_tokens()

        if children.next_token.has("alias"):
            return children.make("AliasStatement")

        if children.next_token.has("assert"):
            return children.make("StaticAssertStatement")

        if children.next_token.has("static"):
            static = children.take()

            if not children.next_token.has("assert"):
                children.unignore()
                children.nodes = children.nodes[:-1]
            else:
                children = NodeChildren(children.parser)
                children += static
                return children.make("StaticAssertStatement", children)

        if children.next_token_may_be_type:
            children.make("Declaration")
        else:
            children.make("Expression")

            if not children.next_token.has("\n", ""):
                children.unignore()
                children.nodes = children.nodes[:-1]
                children.make("Declaration")

        children.take_comments()
        children.expecting_has("\n", "")
        children.ignore_format_tokens()

        return cls(children)
