from abc import ABC, abstractmethod
from util.misc import last_enumerate

class Node(ABC):
    @property
    @abstractmethod
    def nodes(self):
        pass

    def __repr__(self):
        return self.tree_repr("     ")

    def tree_repr(self, prefix):
        string = f"{type(self).__name__}\n"

        for at_last, node in last_enumerate(self.nodes):
            symbol = "└──" if at_last else "├──"
            new_prefix = f"{prefix}{'' if at_last else '│'}    "
            string += f"{prefix}{symbol} {node.tree_repr(new_prefix)}"

        return string

    def mark(self):
        for node in self.nodes:
            node.mark()

    @classmethod
    @abstractmethod
    def construct(cls, parser):
        pass

    @abstractmethod
    def transpile(self, transpiler):
        pass

class PrimaryNode(Node):
    @property
    def nodes(self):
        return [self.token, *self.tokens]

    def __init__(self, token, *tokens):
        self.token = token
        self.tokens = tokens

    def tree_repr(self, prefix):
        tokens = [self.token, *self.tokens] if len(self.tokens) > 0 else self.token
        return f"{type(self).__name__} {tokens}"

class BinaryOperation(Node):
    @property
    def nodes(self):
        return [self.left, self.operator, self.right]

    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    @classmethod
    def construct_binary(cls, parser, has_list, right):
        pass
