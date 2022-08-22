from .identifier_declaration import IdentifierDeclaration

class VariableDeclaration(IdentifierDeclaration):
    @classmethod
    def construct(cls):
        if cls.parser.next.has("var"):
            cls.parser.take()

        return super().construct()

    def transpile_name(self, keyword, name):
        return self.transpiler.symbols.new_variable(self, keyword, name)
