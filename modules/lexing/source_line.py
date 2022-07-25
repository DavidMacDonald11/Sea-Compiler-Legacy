from .token import Token

class SourceLine:
    @property
    def next(self):
        return SourceLine(self.number + 1)

    @property
    def string_remainder(self):
        return self.string[self._locale[1]:]

    def __init__(self, number = 1):
        self.number = number
        self.string = ""
        self.tokens = []
        self.marks = []
        self._locale = [0, 0]

    def __iadd__(self, other):
        if isinstance(other, str):
            self.string += other
            return self

        if isinstance(other, Token):
            self.tokens += [other]
            other.locale = self._locale.copy()
            self._locale[0] = self._locale[1]
            return self

        raise NotImplementedError(f"Cannot iadd {type(other).__name__} to SourceLine")

    def __eq__(self, other):
        if isinstance(other, str):
            return self.string == other

        if isinstance(other, SourceLine):
            return self.number == other.number

        raise NotImplementedError(f"Cannot compare {type(other).__name__} to SourceLine")

    def __repr__(self):
        return repr(self.tokens)

    def ignore(self):
        self._locale[0] = self._locale[1]

    def increment(self):
        self._locale[1] += 1

    def mark(self, token):
        self.marks += [token.locale]

    def last_was_slash(self):
        taken = self.string[self._locale[0]:self._locale[1]]
        taken = taken.replace(r"\\", "")

        return len(taken) > 1 and taken[-1] == "\\"

    def raw(self):
        col1, col2 = -1, -1

        for locale in self.marks:
            if col1 < 0 or locale[0] < col1:
                col1 = locale[0]

            if col2 < 0 or locale[1] > col2:
                col2 = locale[1]

        string = f"{self.number:4d}|{self.string}"
        string += "    |"
        string += "".join(" " if i < col1 or i > col2 else "^" for i in range(col2))

        return f"{string}\n"
