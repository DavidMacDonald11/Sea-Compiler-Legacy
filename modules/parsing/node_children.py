from lexing.token import Token
from util.misc import last_enumerate
from.node import Node

class NodeChildren:
    def __init__(self):
        self.nodes = []

    def __iadd__(self, other):
        if isinstance(other, (Token, Node)):
            self.nodes += [other]
        else:
            raise NotImplementedError(f"Cannot add {type(other)} to TokenList.")

        return self

    def __repr__(self):
        string = ""

        for at_last, node in last_enumerate(self.nodes):
            symbol = "└──" if at_last else "├──"
            string += f"{symbol} {node}\n"

        return string

    def raw(self):
        return repr(self)
