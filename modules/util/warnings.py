class CompilerWarning:
    def __init__(self, message, component):
        self.message = message
        self.component = component

    def printable(self, prefix = "warning: "):
        return f"{prefix}{self.message}\n{self.component.raw()}"

class CompilerError(CompilerWarning, Exception):
    def printable(self, prefix = "error: "):
        return super().printable(prefix)

class Stop(Exception):
    pass
