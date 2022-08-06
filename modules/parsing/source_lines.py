from lexing.source_line import SourceLine
from lexing.token import Token
from .node import Node

class SourceLines:
    def __init__(self):
        self.lines = []

    def __iadd__(self, other):
        if isinstance(other, Token):
            other = other.line

        if isinstance(other, SourceLine):
            if other not in self.lines:
                self.lines += [other]

            return self

        if isinstance(other, Node):
            for node in other.nodes:
                self += node.line

            return self

        raise NotImplementedError(f"Cannot add {type(other).__name__} to SourceLines")

    def raw(self):
        return "".join(line.raw() for line in self.lines)
