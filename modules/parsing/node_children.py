from lexing.token import Token
from util.misc import last_enumerate, repr_expand
from util.warnings import CompilerWarning, CompilerError
from.node import Node

class NodeChildren:
    @property
    def next_token(self):
        return self.parser.token

    def __init__(self, parser):
        self.parser = parser
        self.lines = []
        self.nodes = []

    def __iadd__(self, other):
        if isinstance(other, Token):
            self.nodes += [other]
            self.add_line(other.line)
            return self

        if isinstance(other, Node):
            self.nodes += [other]

            for line in other.children.lines:
                self.add_line(line)

            return self

        raise NotImplementedError(f"Cannot add {type(other)} to TokenList.")

    def __repr__(self):
        return self.tree_repr()

    def tree_repr(self, prefix = ""):
        string = ""

        for at_last, node in last_enumerate(self.nodes):
            symbol = "└──" if at_last else "├──"
            new_prefix = f"{prefix}{'' if at_last else '│'}    "
            string += f"{prefix}{symbol} {node.tree_repr(new_prefix)}"

        return string

    def add_line(self, line):
        if line not in self.lines:
            self.lines += [line]

    def warn(self, message):
        self.parser.warnings += [CompilerWarning(message, self)]

    def take(self):
        taken = self.parser.token
        self.parser.i += 1
        self += taken

        return taken

    def take_and_warn(self, message):
        taken = self.take()
        taken.line.mark(taken)
        self.warn(message)

        return taken

    def ignore(self):
        self.parser.i += 1

    def expecting_error(self, *things):
        token = self.parser.token
        token.line.mark(token)

        things = repr_expand(things)
        raise CompilerError(f"Expecting {things}", self)

    def expecting_of(self, *kinds):
        if self.parser.token.of(*kinds):
            return self.take()

        self.expecting_error(*kinds)

    def expecting_has(self, *strings):
        if self.parser.token.has(*strings):
            return self.take()

        self.expecting_error(*strings)

    def make(self, kind):
        node = self.parser.make(kind)
        self += node
        return node

    def raw(self):
        string = f"{self.lines[0].filename}:\n"
        string += "".join(line.raw() for line in self.lines)

        return string

    def next(self):
        return NodeChildren(self.parser)
