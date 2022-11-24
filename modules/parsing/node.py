from abc import ABC, abstractmethod
from util.misc import last_enumerate, set_add

class Node(ABC):
    parser = None
    c_transpiler = None

    @property
    @abstractmethod
    def nodes(self) -> list:
        pass

    @property
    def transpiler(self):
        return type(self).c_transpiler

    @property
    def indent(self):
        return "\t" * self.transpiler.context.blocks

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

    def lines(self):
        lines = []

        for node in self.nodes:
            set_add(lines, node.lines() if isinstance(node, Node) else [node.line])

        return lines

    def raw(self):
        return "".join(line.raw() for line in self.lines())

    def of(self, *kinds):
        return isinstance(self, kinds)

    @classmethod
    @abstractmethod
    def construct(cls):
        pass

    @abstractmethod
    def transpile(self):
        pass

class PrimaryNode(Node):
    @property
    def nodes(self) -> list:
        return [self.token, *self.tokens]

    @classmethod
    def construct(cls):
        return cls(cls.parser.take())

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

    def transpile(self):
        return self.transpile_binary(self.operator.string)

    def transpile_binary(self, operator, bitwise = False, boolean = False):
        left = self.left.transpile().operate(self)
        right = self.right.transpile().operate(self)
        result = self.transpiler.expression.resolve(left, right).cast_up()

        if not boolean and not bitwise:
            return result.new(f"{left} {operator} {right}")

        if bitwise:
            if result.e_type not in ("f64", "fmax", "g64", "gmax", "c64", "cmax"):
                return result.new(f"{left} {operator} {right}")

            message = "Cannot perform bitwise operation on floating type"
            self.transpiler.warnings.error(self, message)
            return result.new(f"{left} /*{operator} {right}*/")

        if not left.e_type == right.e_type == "bool":
            self.transpiler.warnings.error(self, "".join((
                f"Cannot perform boolean operation '{self.operator.token}' on non-boolean type. ",
                "(Consider using the '?' operator to get boolean value)")))

            return result.new(f"{left} /*{self.operator.token} {right}*/")

        return result.new(f"{left} {operator} {right}").cast("bool")
