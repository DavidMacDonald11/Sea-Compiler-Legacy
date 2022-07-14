class TokenString:
    def __init__(self, filename, symbols, begin, end = None):
        self.filename = filename
        self.symbols = symbols
        self.begin = begin
        self.end = end if end is not None else begin.copy()

    def __iadd__(self, symbol):
        self.symbols += symbol

        if symbol != "\n":
            self.end[0] += 1
            return self

        self.end[0] = 1
        self.end[1] += 1

        return self

    def __add__(self, obj):
        result = self.copy()

        for _ in range(obj.start[0] - self.end[0]):
            result += " "

        for symbol in self.symbols:
            result += symbol

        return result

    def __repr__(self):
        file = f"{self.filename}"
        begin = f"Ln{self.begin[1]}, Col {self.begin[0]}"
        end = f"Ln {self.end[1]}, Col {self.end[0]}"

        location = f"{file}: {begin} to {end}"
        lines = ""

        for i, line in enumerate(self.symbols.split("\n")):
            num = i + self.begin[1]
            lines += f"{num:4d} | {line}\n"

        return f"{file}: {begin} to {end}\n{lines}"

    def copy(self):
        position = (self.begin.copy(), self.end.copy())
        return TokenString(self.filename, self.symbols, *position)

    def next(self):
        return TokenString(self.filename, "", self.end.copy())
