import re
from string import ascii_letters
from util.warnings import CompilerError
from .token import Token

class Identifier(Token):
    START = f"{ascii_letters}_\\"

    def validate(self, symbols):
        pattern = re.compile(r"^(\w*\\((u[0-9A-F]{4})|(U[0-9A-F]{8})))*\w*$")

        if not pattern.match(symbols):
            raise CompilerError("Incorrect identifier", self.string)