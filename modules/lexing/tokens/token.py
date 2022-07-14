class Token:
    @property
    def symbols(self):
        return self.string.symbols

    def __init__(self, string):
        self.string = string
        self.validate(string.symbols)

    def __repr__(self):
        symbols = self.symbols.replace("\n", r"\n").replace("    ", r"\t")
        symbols = "EOF" if symbols == "" else symbols
        return f"{type(self).__name__[0]}'{symbols}'"

    def validate(self, symbols):
        pass
