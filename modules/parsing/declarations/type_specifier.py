from util.warnings import CompilerError
from ..node import Node

class TypeSpecifier(Node):
    @classmethod
    def construct(cls, children):
        specifier = children.next_token

        if specifier.has("auto", "void", "str") or specifier.of("Identifier"):
            children.take()
            return cls(children)

        if children.next_token.has("func"):
            children.take()
            children.expecting_has("(")
            children.expecting_has("(")
            # TODO function variadic list opt
            children.expecting_has(")")

            if children.next_token.has("->"):
                children.take().kind = "Punctuator"
                children.make("TypeName")

            children.expecting_has(")")

            return cls(children)

        if children.next_token.has("complex", "imaginary", "real"):
            children.take()

        unsigned = children.take() if children.next_token.has("+") else None

        if unsigned is not None:
            unsigned.kind = "Punctuator"

        if children.next_token.has("bool", "char", "int", "float"):
            taken = children.take()

            if unsigned and taken.has("float"):
                unsigned.mark()
                taken.mark()
                children.warn("Cannot declare unsigned float")

            return cls(children)

        if children.next_token.has("short", "long", "double"):
            prefix = children.take()

            if unsigned and prefix.has("double"):
                unsigned.mark()
                prefix.mark()
                children.warn("Cannot declare unsigned double")

            if children.next_token.has("int", "float"):
                postfix = children.take()

                if prefix.has("short", "long") and postfix.has("float"):
                    prefix.mark()
                    postfix.mark()
                    children.warn(f"Cannot declare {prefix} float")
                elif prefix.has("double") and postfix.has("int"):
                    prefix.mark()
                    postfix.mark()
                    children.warn("Cannot declare double int")

        if len(children.nodes) == 0:
            token = children.take()
            token.mark()
            raise CompilerError(f"Unexpected token {token}", children)

        return cls(children)
