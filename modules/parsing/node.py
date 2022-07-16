from abc import ABC, abstractmethod

class Node(ABC):
    def __init__(self, children):
        self.children = children

    def __repr__(self):
        return f"{type(self).__name__}\n{repr(self.children)}"

    @classmethod
    @abstractmethod
    def construct(cls, parser):
        pass

    # TODO uncomment
    #@abstractmethod
    def transpile(self):
        pass
