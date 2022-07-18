from abc import ABC, abstractmethod
from functools import wraps

class Node(ABC):
    def __init__(self, children, specifier = None):
        self.children = children
        self.specifier = specifier

    def __repr__(self):
        return self.tree_repr()

    def tree_repr(self, prefix = "     "):
        name = type(self).__name__
        return f"{name}\n{self.children.tree_repr(prefix)}"

    def mark(self):
        for node in self.children.nodes:
            node.mark()

    @classmethod
    @abstractmethod
    def construct(cls, children):
        pass

    # TODO uncomment
    #@abstractmethod
    def transpile(self):
        pass

def binary_operation(has_list, right):
    def decorator(func):
        @wraps(func)
        def construct(cls, children):
            def recursive_construct(children, head):
                children = children.next()
                children += head

                if not children.next_token.has(*has_list):
                    return head

                func(cls, children)

                children.take()
                children.make(right)

                return recursive_construct(children, cls(children))

            return recursive_construct(children, children.make(right))

        return construct
    return decorator
