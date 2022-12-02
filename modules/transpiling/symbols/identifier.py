from .symbol import Symbol

class Identifier(Symbol):
    @property
    def c_name(self):
        raise NotImplementedError(type(self).__name__)

    def __init__(self, name, kind, table_number):
        self.kind = kind
        self.table_number = table_number
        super().__init__(name)
