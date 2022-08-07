from .source_line import SourceLine

class SourceFile:
    @property
    def next(self):
        string = self.line.unread_string
        return string[0] if string != "" else ""

    def __init__(self, filepath):
        self.filepath = filepath
        self.file = open(filepath, "r", encoding = "UTF-8")
        self.line = None

        self.read_line()

    def __del__(self):
        self.file.close()

    def read_line(self):
        self.line = SourceLine() if self.line is None else self.line.next()
        symbol = "\0"

        while symbol not in "\n":
            symbol = self.file.read(1)
            self.line += symbol

    def take(self, num = -1, these = "", until = ""):
        string = ""

        if self.line == "" or num == 0:
            return string

        for char in self.line.unread_string:
            if char in until or these != "" and char not in these:
                return string

            string += char
            self.line.increment()

            if num > 0 and len(string) == num:
                break

        if self.line.unread_string == "" and self.line != "":
            self.read_line()

        return string
