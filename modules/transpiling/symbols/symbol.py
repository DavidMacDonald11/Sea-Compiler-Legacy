class Symbol:
    @property
    def c_name(self):
        raise NotImplementedError(type(self).__name__)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.c_name
