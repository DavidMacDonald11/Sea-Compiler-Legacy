from util.warnings import CompilerWarning
from .node_map import NODE_MAP
from .source_lines import SourceLines

class Parser:
    @property
    def next(self):
        if self.i >= len(self.tokens):
            self.i = len(self.tokens) - 1

        return self.tokens[self.i]

    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0
        self.depth = 0
        self.lines = SourceLines()
        self.saved = [0, None]
        self.tree = None
        self.warnings = []

    def warn(self, message):
        self.warnings += [CompilerWarning(message, self.lines)]

    def take(self, of = None, has = None):
        if isinstance(of, str):
            of = [of]

        if of is not None and not self.next.of(*of):
            return None

        if isinstance(has, str):
            has = [has]

        if has is not None and not self.next.has(*has):
            return None

        token = self.next
        self.i += 1
        self.lines += token

        return token

    def make(self, kind, depth = 0):
        lines = self.lines
        self.lines = SourceLines()

        node = NODE_MAP[kind].construct(self)

        self.lines = lines



    def set_state(self):
        self.saved = [self.i, self.lines.lines]

    def reset_state(self):
        self.i, self.lines.lines = self.saved
