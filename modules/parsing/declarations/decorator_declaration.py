from ..node import Node

class DecoratorDeclaration(Node):
    @classmethod
    def construct(cls, children):
        if not children.next_token.has("decorate"):
            return None

        children.take()
        children.expecting_has("with")

        empty = True

        while children.next_token.of("Identifier"):
            empty = False
            children.expecting_of("Identifier")

            if children.next_token.has("("):
                children.take()

                if children.next_token.has(")"):
                    children.take()

                    if children.next_token.has(","):
                        children.take()

                    continue

                children.make("AssignmentExpression")

                while children.next_token.has(","):
                    children.take()

                    if children.next_token.has(")"):
                        children.take_and_warn("Expecting assignment-expression")
                        break

                    children.make("AssignmentExpression")

                children.expecting_has(")")

            if children.next_token.has(","):
                children.take()

        children.expecting_line_end()
        node = cls(children)

        if empty:
            node.mark()
            children.warn("Cannot have empty decorator")

        return node
