class CompilerWarning:
    def __init__(self, message, component):
        self.message = message
        self.component = component

    def printable(self, prefix = "warning: "):
        return f"{prefix}{self.message}\n{repr(self.component)}"

class CompilerError(CompilerWarning, Exception):
    def printable(self, prefix = "error: "):
        return super().printable(prefix)
