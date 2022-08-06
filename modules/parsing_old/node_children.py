from lexing.token import Token
from lexing.source_line import SourceLine
from util.misc import last_enumerate
from .node import Node

class NodeChildren:
    def __init__(self):
        self.lines = []
        self.nodes = []

    def __iadd__(self, other):
        if other is None:
            return self

        if isinstance(other, SourceLine):
            if other not in self.lines:
                self.lines += [other]

            return self

        if isinstance(other, Token):
            self.nodes += [other]
            self += other.line
            return self

        if isinstance(other, Node):
            self.nodes += [other]

            for line in other.children.lines:
                self += line

            return self

        raise NotImplementedError(f"Cannot add {type(other)} to NodeChildren.")

    def __len__(self):
        return len(self.nodes)

    def __repr__(self):
        return self.tree_repr()

    def tree_repr(self, prefix = ""):
        string = ""

        for at_last, node in last_enumerate(self.nodes):
            symbol = "└──" if at_last else "├──"
            new_prefix = f"{prefix}{'' if at_last else '│'}    "
            string += f"{prefix}{symbol} {node.tree_repr(new_prefix)}"

        return string

    def raw(self):
        string = f"{self.lines[0].filename}:\n"
        string += "".join(line.raw() for line in self.lines)

        return string

    def untake(self):
        self.nodes = self.nodes[:-1]
