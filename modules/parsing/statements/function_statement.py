from .function_definition import FunctionDefinition
from .hidden_statement import HiddenStatement

class FunctionStatement(HiddenStatement):
    @classmethod
    def construct(cls):
        statement = FunctionDefinition.construct()
        return None if statement is None else cls(statement)
