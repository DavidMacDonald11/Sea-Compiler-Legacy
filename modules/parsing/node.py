from abc import ABC, abstractmethod

class Node(ABC):
    def __init__(self, children, specifier = None):
        self.children = children
        self.specifier = specifier

    def __repr__(self):
        return self.tree_repr()

    def tree_repr(self, prefix = "     "):
        name = type(self).__name__
        return f"{name}\n{self.children.tree_repr(prefix)}"

    @classmethod
    @abstractmethod
    def construct(cls, children):
        pass

    # TODO uncomment
    #@abstractmethod
    def transpile(self):
        pass
