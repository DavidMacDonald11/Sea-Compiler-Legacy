from util.warnings import CompilerWarning
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
        self.children = NodeChildren()
        self.tree = None
        self.warnings = []

    def warn(self, message):
        self.warnings += [CompilerWarning(message, self.children)]

    def new_node(self, cls):
        node = cls(self.children)
        self.children = NodeChildren()
        return node

    # TODO Refactor node children to work recursively for child nodes

    def make_tree(self):
        self.tree = self.make("PrimaryExpression")

    def make(self, kind):
        return CONSTRUCT_MAP[kind](self)

    def take(self, children = None):
        if children is None:
            children = self.children

        taken = self.token
        self.i += 1
        children += taken

        return taken
