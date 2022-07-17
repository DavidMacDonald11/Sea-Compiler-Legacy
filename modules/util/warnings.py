class CompilerWarning:
    def __init__(self, message, component):
        self.message = message
        self.component = component

    def printable(self, prefix = "warning: "):
        string = f"{prefix}{self.message}\n"
        string += "" if self.component is None else self.component.raw()

        return string

class CompilerError(CompilerWarning, Exception):
    def printable(self, prefix = "error: "):
        return super().printable(prefix)

class Stop(Exception):
    pass
