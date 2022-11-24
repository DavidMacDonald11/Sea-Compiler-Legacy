from .statement import Statement
from ..node import Node

class FileStatement(Node):
    @property
    def nodes(self) -> list:
        return self.statements

    def __init__(self):
        self.statements = []

    @classmethod
    def construct(cls):
        return cls()

    def make_tree(self, parser):
        while not parser.next.has("EOF"):
            self.statements += [Statement.construct()]

    def transpile(self):
        for statement in self.statements:
            statement.transpile()

        self.transpiler.symbols.verify_called_functions()
