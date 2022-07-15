from functools import cached_property

class TokenString:
    def __init__(self, filename, symbols, begin, end = None):
        self.line = ""
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
        col1, ln1 = self.begin
        col2, ln2 = self.end

        file = f"{self.filename}"
        location = f"Ln{ln1}, Col {col1} to Col {col2}"
        line1 = f"{ln1:4d}|{self.line}"
        line2 = "    |" + " " * (col1 - 1) + "^" * (col2 - col1)

        return f"{file}: {location}\n{line1}{line2}\n"

    def copy(self):
        position = (self.begin.copy(), self.end.copy())
        string = TokenString(self.filename, self.symbols, *position)
        string.line = self.line

        return string

    def next(self, lines):
        string = TokenString(self.filename, "", self.end.copy())
        string.line = lines[self.end[1] - 1]
        return string
