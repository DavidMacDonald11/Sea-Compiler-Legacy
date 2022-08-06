from util.warnings import CompilerError
from ..node import Node

class FileStatement(Node):
    def construct(self, parser):
        while not parser.next.has(""):
            try:
                parser.make("Statement")
            except CompilerError as error:
                for node in error.component.nodes:
                    parser.children += node

                raise error

        parser.take()
        return self
