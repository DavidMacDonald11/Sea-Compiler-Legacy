from lexing.token import Token
from parsing.node import Node

class Warnings:
    def __init__(self):
        self.warnings = []
        self.errors = []
        self.failure = ""

    def __repr__(self):
        return "\n".join(self.warnings + self.errors) + self.failure

    def _add(self, component, message, label):
        string = ""

        if isinstance(component, Token):
            component.mark()
            string = component.line.raw()
        elif isinstance(component, Node):
            component.mark()
            string = component.raw()
        elif component is not None:
            raise NotImplementedError(f"Must define Warnings.add(: {type(component).__name__})")

        string = f"{label}: {message}\n{string}"

        match label:
            case "warning":
                self.warnings += [string]
            case "error":
                self.errors += [string]
            case "failure":
                self.failure = string

    def warn(self, component, message):
        self._add(component, message, "warning")

    def error(self, component, message):
        self._add(component, message, "error")

    def fail(self, component, message):
        self._add(component, message, "failure")
        return Warnings.CompilerFailure()

    def check(self):
        if len(self.warnings + self.errors) > 0:
            raise Warnings.CompilerFailure()

    class CompilerFailure(Exception):
        pass
