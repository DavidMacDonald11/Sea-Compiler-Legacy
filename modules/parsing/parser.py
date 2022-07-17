from util.warnings import CompilerError
from .make import CONSTRUCT_MAP
from .node_children import NodeChildren

class Parser:
    @property
    def token(self):
        if self.i >= len(self.tokens):
            self.i = len(self.tokens) - 1

        return self.tokens[self.i]

    def __init__(self, tokens):
        self.i = 0
        self.tokens = tokens
        self.tree = None
        self.warnings = []

    def make_tree(self):
        self.tree = self.make("FileStatement")
        children = self.tree.children

        while not children.next_token.has(""):
            try:
                children.make("Statement")
            except CompilerError as error:
                for node in error.component.nodes:
                    children += node

                raise error

        children.take()

    def make(self, kind):
        return CONSTRUCT_MAP[kind](NodeChildren(self))
