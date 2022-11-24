class Context:
    def __init__(self):
        self.blocks = 0
        self.loops = 0
        self.calls = 0
        self.in_return = False
        self.function = None

    @property
    def in_block(self):
        return self.blocks > 0

    @property
    def in_loop(self):
        return self.loops > 0

    @property
    def in_call(self):
        return self.calls > 0

    @property
    def in_function(self):
        return self.function is not None

    @property
    def hide_imag(self):
        return self.in_call or self.in_return and "imag" in self.function.return_type
