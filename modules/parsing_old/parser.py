from util.misc import repr_expand
from util.warnings import CompilerError, CompilerWarning
from .make import NODE_MAP
from .node_children import NodeChildren

class Parser:
    tokens = []
    index = 0
    tree = None
    warnings = []

    @classmethod
    def set(cls, tokens):
        cls.tokens = tokens
        cls.index = 0
        cls.tree = None
        cls.warnings = []

    @classmethod
    def make_tree(cls):
        cls.tree = cls().make("FileStatement")

    @property
    def next(self):
        cls = type(self)

        if cls.index >= len(cls.tokens):
            cls.index = len(cls.tokens) - 1

        return cls.tokens[cls.index]

    def __init__(self, children = None, depth = 0):
        self.children = NodeChildren() if children is None else children
        self.depth = depth

    def new(self, depth = 0):
        return Parser(depth = self.depth + depth)

    def warn(self, message):
        type(self).warnings += [CompilerWarning(message, self.children)]

    def take(self):
        token = self.next
        type(self).index += 1
        self.children += token

        return token

    def take_and_warn(self, message):
        token = self.take()
        token.mark()
        self.warn(message)

        return token

    def take_previous(self):
        self.unignore()
        return self.take()

    def take_any_comments(self):
        while self.next.of("Annotation"):
            self.take()

    def untake(self):
        self.unignore()
        self.children.untake()

    def ignore(self):
        type(self).index += 1

    def unignore(self):
        type(self).index -= 1

    def make(self, kind, parser = None, depth = 0):
        parser = Parser(depth = self.depth + depth) if parser is None else parser
        node = NODE_MAP[kind](parser).construct(parser)

        if parser.children is not self.children:
            self.children += node

        return node

    def expecting_error(self, *things):
        self.next.mark()
        raise CompilerError(f"Expecting {repr_expand(things)}", self.children)

    def expecting_of(self, *kinds):
        if self.next.of(*kinds):
            return self.take()

        self.expecting_error(*kinds)

    def expecting_has(self, *strings):
        if self.next.has(*strings):
            return self.take()

        self.expecting_error(*strings)

    def expecting_indent(self, atleast = False):
        tabs = ("\t", " " * 4)

        for _ in range(self.depth):
            if self.next.has(*tabs):
                self.take()
            else:
                self.next.mark()
                self.warn(f"Insufficient indentation; expected {self.depth}")

        if not self.next.has(*tabs):
            return

        while self.next.has(*tabs):
            token = self.take()

            if not atleast:
                token.mark()

        if not atleast:
            self.warn(f"Unexpected indentation; expected {self.depth}")

    def expecting_line_end(self):
        self.take_any_comments()
        return self.expecting_has("\n", "")

    def take_if_empty_line(self):
        i = type(self).index
        parser = self.new()

        while parser.next.has("\t", " " * 4):
            parser.take()

        if parser.next.of("Annotation"):
            parser.take()

        if parser.next.has("\n", ""):
            parser.take()

            for node in parser.children.nodes:
                self.children += node

            return parser

        type(self).index = i
        return None

    def take_any_empty_lines(self):
        empty = self.take_if_empty_line()

        while empty is not None and not self.next.has(""):
            for node in empty.children.nodes:
                self.children += node

            empty = self.take_if_empty_line()

    def indent_count(self):
        i = type(self).index
        parser = self.new()

        while parser.next.has("\t", " " * 4):
            parser.take()

        type(self).index = i
        return len(parser.children)
