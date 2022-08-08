from abc import ABC, abstractmethod
from util.misc import last_enumerate

class Node(ABC):
    parser = None

    @property
    @abstractmethod
    def nodes(self) -> list:
        pass

    def __repr__(self):
        return self.tree_repr("     ")

    def tree_repr(self, prefix):
        string = f"{type(self).__name__}"

        for at_last, node in last_enumerate(self.nodes):
            symbol = "└──" if at_last else "├──"
            new_prefix = f"{prefix}{'' if at_last else '│'}    "
            string += f"\n{prefix}{symbol} {node.tree_repr(new_prefix)}"

        return string

    def mark(self):
        for node in self.nodes:
            node.mark()

    def raw(self):
        return "".join(n.raw() if isinstance(n, Node) else n.line.raw() for n in self.nodes)

    @classmethod
    @abstractmethod
    def construct(cls):
        pass

    #TODO@abstractmethod
    def transpile(self, transpiler):
        pass

class PrimaryNode(Node):
    @property
    def nodes(self) -> list:
        return [self.token, *self.tokens]

    def __init__(self, token, *tokens):
        self.token = token
        self.tokens = tokens

    def tree_repr(self, prefix):
        tokens = [self.token, *self.tokens] if len(self.tokens) > 0 else self.token
        return f"{type(self).__name__} ── {tokens}"

class BinaryOperation(Node):
    @property
    def nodes(self) -> list:
        return [self.left, self.operator, self.right]

    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    @classmethod
    def construct_binary(cls, has_list, default, right = None):
        if right is None:
            right = default

        node = default.construct()

        if not cls.parser.next.has(*has_list):
            return node

        while cls.parser.next.has(*has_list):
            operator = cls.parser.take()
            node = cls(node, operator, right.construct())

        return node

    def transpile(self, transpiler):
        return self.transpile_binary(transpiler, self.operator.string)

    def transpile_binary(self, transpiler, operator):
        left = self.left.transpile(transpiler)
        right = self.right.transpile(transpiler)
        return f"{left} {operator} {right}"
