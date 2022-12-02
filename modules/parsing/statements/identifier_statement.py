from .variable_definition import VariableDefinition
from .invariable_definition import InvariableDefinition
from .hidden_statement import HiddenStatement

class IdentifierStatement(HiddenStatement):
    @classmethod
    def construct(cls):
        definition = InvariableDefinition if cls.parser.next.has("invar") else VariableDefinition
        statement = definition.construct()

        return cls(statement)
