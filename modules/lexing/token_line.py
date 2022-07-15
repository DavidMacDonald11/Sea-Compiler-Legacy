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

        raise NotImplementedError(f"Cannot compare {type(other)} to TokenLine.")

    def __repr__(self):
        return repr(self.tokens)

    def ignore(self):
        self.locale[0] = self.locale[1]

    def increment(self):
        self.locale[1] += 1
