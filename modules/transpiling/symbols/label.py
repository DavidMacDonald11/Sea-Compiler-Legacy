from .symbol import Symbol
from ..expression import Expression
from ..statement import Statement

class Label(Symbol):
    @property
    def c_name(self):
        return f"__sea_label_{self.name}"

    def surround(self, statement):
        statement.prefix(Expression("", f"{self.c_name}_continue__:"))
        statement.append(Statement(Expression("", f"{self.c_name}_break__:")))

        return statement
