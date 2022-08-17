from .identifier_declaration import IdentifierDeclaration

class InvariableDeclaration(IdentifierDeclaration):
    @classmethod
    def construct(cls):
        cls.parser.expecting_has("invar")
        return super().construct()

    def transpile_name(self, sea_keyword, sea_name):
        return self.transpiler.symbols.new_invariable(sea_keyword, sea_name)
