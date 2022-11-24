class Identifier:
    @property
    def c_name(self):
        raise NotImplementedError(type(self).__name__)

    def __init__(self, s_type, name, table_number):
        self.s_type = s_type
        self.name = name
        self.table_number = table_number

    def __repr__(self):
        return self.c_name
