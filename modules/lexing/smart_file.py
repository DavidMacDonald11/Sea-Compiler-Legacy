from .token_line import TokenLine

class SmartFile:
    @property
    def next(self):
        string = self.line.string
        return string[self.i] if self.i < len(string) else ""

    def __init__(self, filepath):
        self.filepath = filepath
        self.file = open(filepath, "r", encoding = "UTF-8")
        self.line = None
        self.lines = 0
        self.i = 0

        self.read_line()

    def __del__(self):
        self.file.close()

    def read_line(self):
        self.lines += 1
        self.line = TokenLine(self.filepath, self.lines)
        symbol = "\0"

        while symbol not in "\n":
            symbol = self.file.read(1)
            self.line += symbol

    def take(self, num = -1, these = "", until = ""):
        string = ""

        if self.line == "" or num == 0:
            return string

        for i, char in enumerate(self.line.string[self.i:], self.i):
            if char in until or these != "" and char not in these:
                return string

            string += char
            self.i = i + 1
            self.line.increment()

            if num > 0 and len(string) == num:
                break

        if self.i >= len(self.line.string):
            self.i = 0
            self.read_line()

        return string
