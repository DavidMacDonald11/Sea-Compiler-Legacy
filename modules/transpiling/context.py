class Context:
    def __init__(self):
        self.blocks = 0
        self.loops = 0
        self.in_return = False
        self.in_ownership = False
        self.function = None
        self.array = None

    @property
    def in_block(self):
        return self.blocks > 0

    @property
    def in_loop(self):
        return self.loops > 0

    @property
    def in_function(self):
        return self.function is not None
