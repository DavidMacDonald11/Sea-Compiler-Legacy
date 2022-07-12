class FileSymbols:
    def __init__(self, filename, symbols, begin, end = None):
        self.filename = filename
        self.symbols = symbols
        self.begin = begin
        self.end = end if end is not None else begin.copy()

    def __iadd__(self, symbol):
        if symbol != "\n":
            self.symbols[-1] += symbol
            self.end[0] += 1
            return

        self.symbols += [""]
        self.end[0] = 1
        self.end[1] += 1

    def __add__(self, obj):
        result = self.copy()

        for line in symbols:
            for symbol in line:
                result += symbol

            result += "\n"

        return result

    def __repr__(self):
        file = f"{self.filename}"
        begin = f"Ln{self.begin[1]}, Col {self.begin[0]}"
        end = f"Ln {self.end[1]}, Col {self.end[0]}"

        location = f"{file}: {begin} to {end}"
        lines = ""

        for i, line in enumerate(self.lines):
            num = i + self.begin[1]
            lines += f"{num:4d} |{line}\n"


        return f"{file}: {begin} to {end}\n{lines}"

    def copy(self):
        position = (self.begin.copy(), self.end.copy())
        return FileSymbols(self.filename, self.symbols.copy(), *position)

    def next(self):
        return FileSymbols(self.filename, [""], self.end.copy())
