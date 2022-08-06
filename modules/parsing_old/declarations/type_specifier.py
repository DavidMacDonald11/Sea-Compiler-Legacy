from util.warnings import CompilerError
from ..node import Node

class TypeSpecifier(Node):
    def construct(self, parser):
        if parser.next.has("auto", "void", "str") or parser.next.of("Identifier"):
            parser.take()
            return self

        if parser.next.has("func"):
            return self.construct_function(parser)

        if parser.next.has("complex", "imaginary", "real"):
            parser.take()

        unsigned = parser.take() if parser.next.has("+") else None

        if unsigned is not None:
            unsigned.kind = "Punctuator"

        if parser.next.has("bool", "char", "int", "float"):
            taken = parser.take()

            if unsigned is not None and taken.has("float"):
                unsigned.mark()
                taken.mark()
                parser.warn("Cannot declare unsigned float")

            return self

        if parser.next.has("short", "long", "double"):
            prefix = parser.take()

            if unsigned is not None and prefix.has("double"):
                unsigned.mark()
                prefix.mark()
                parser.warn("Cannot declare unsigned double")

            if parser.next.has("int", "float"):
                postfix = parser.take()

                if prefix.has("short", "long") and postfix.has("float"):
                    prefix.mark()
                    postfix.mark()
                    parser.warn(f"Cannot declare {prefix} float")
                elif prefix.has("double") and postfix.has("int"):
                    prefix.mark()
                    postfix.mark()
                    parser.warn("Cannot declare double int")

        if len(parser.children) == 0:
            token = parser.take()
            token.mark()
            raise CompilerError(f"Unexpected type specifier {token}", parser.children)

        return self

    def construct_function(self, parser):
        parser.take()
        parser.expecting_has("(")
        parser.expecting_has("(")

        if not parser.next.has(")"):
            parser.make("FunctionVariadicList")

        parser.expecting_has(")")

        if parser.next.has("->"):
            parser.take().kind = "Punctuator"
            parser.make("TypeName")

        parser.expecting_has(")")

        self.specifier = "Func"
        return self
