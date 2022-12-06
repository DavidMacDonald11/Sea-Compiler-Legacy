from .expression import Expression

class Statement:
    cached = []

    @property
    def expression(self):
        return self.lines[-1]

    def __init__(self, expression = None):
        self.lines = [*type(self).cached, expression or Expression()]
        type(self).cached = []

    def show_kind(self):
        for line in self.lines:
            line.show_kind()

        return self

    def finish(self, node, semicolons = True):
        for line in self.lines:
            line.finish(node, semicolons)

        return self

    def prefix(self, expression):
        self.lines = [*self.lines[:-1], expression, self.lines[-1]]
        return self

    def new_prefix(self, statement):
        self.lines = [*statement.lines[:-1], *self.lines]
        self.lines[-1] = statement.lines[-1]
        return self

    def append(self, statement = None):
        if statement is None:
            self.lines += [Expression()]
        else:
            self.lines += [*statement.lines, Expression()]

        return self

    def new_append(self, statement):
        self.lines[-1] = statement.lines[0].add(self.expression.string)
        self.lines += [*statement.lines[1:], Expression()]
        return self

    def drop(self):
        self.lines = self.lines[:-1]
        return self

    def new(self, string):
        self.expression.new(string)
        return self

    def add(self, before = "", after = ""):
        self.expression.add(before, after)
        return self

    def cast(self, kind):
        self.expression.cast(kind)
        return self
