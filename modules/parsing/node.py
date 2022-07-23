from abc import ABC, abstractmethod
from functools import wraps

class Node(ABC):
    def __init__(self, parser):
        self.parser = parser
        self.children = parser.children
        self.specifier = None

    def __repr__(self):
        return self.tree_repr()

    def tree_repr(self, prefix = "     "):
        name = type(self).__name__
        return f"{name}\n{self.children.tree_repr(prefix)}"

    def mark(self):
        for node in self.children.nodes:
            node.mark()

    @abstractmethod
    def construct(self, parser):
        pass

    def transpile(self, transpiler):
        pass

    @classmethod
    def binary_operation(cls, has_list, right):
        def decorator(func):
            @wraps(func)
            def construct(self, parser):
                def recursive_construct(parser, node):
                    parser = parser.new()
                    parser.children += node

                    if not parser.next.has(*has_list):
                        return node

                    func(self, parser)

                    parser.take()
                    parser.make(right)

                    return recursive_construct(parser, type(self)(parser))

                return recursive_construct(parser, parser.make(right))

            return construct
        return decorator
