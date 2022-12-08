from .line_statement import LineStatement
from .if_statement import IfStatement
from .while_statement import WhileStatement
from .do_while_statement import DoWhileStatement
from .for_statement import ForStatement
from .function_statement import FunctionStatement
from .hidden_statement import HiddenStatement

class Statement(HiddenStatement):
    @classmethod
    def construct(cls):
        if cls.parser.next.has(r"\n"):
            cls.parser.take()

        statement = IfStatement.construct() or WhileStatement.construct()
        statement = statement or DoWhileStatement.construct()
        statement = statement or ForStatement.construct()
        statement = statement or FunctionStatement.construct()
        statement = statement or LineStatement.construct()

        return cls(statement)

    def transpile(self):
        for line in self.statement.transpile().lines:
            self.transpiler.write(f"{line}")
