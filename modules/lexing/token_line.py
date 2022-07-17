from .token import Token

class TokenLine:
    @property
    def captured(self):
        return self.string[self.locale[0]:self.locale[1]]

    def __init__(self, filename, number):
        self.filename = filename
        self.number = number
        self.string = ""
        self.tokens = []
        self.locale = [0, 0]
        self.marks = []

    def __iadd__(self, other):
        if isinstance(other, str):
            self.string += other
        elif isinstance(other, Token):
            self.tokens += [other]
            other.locale = self.locale.copy()
            self.locale[0] = self.locale[1]
        else:
            raise NotImplementedError(f"Cannot add {type(other)} to TokenLine.")

        return self

    def __eq__(self, other):
        if isinstance(other, str):
            return self.string == other

        if isinstance(other, TokenLine):
            return self.number == other.number

        raise NotImplementedError(f"Cannot compare {type(other)} to TokenLine.")

    def __repr__(self):
        return repr(self.tokens)

    def ignore(self):
        self.locale[0] = self.locale[1]

    def increment(self):
        self.locale[1] += 1

    def mark(self, token):
        self.marks += [token.locale]

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
