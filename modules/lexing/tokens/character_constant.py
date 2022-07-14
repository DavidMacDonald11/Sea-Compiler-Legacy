import re
from util.warnings import CompilerError
from .token import Token

class CharacterConstant(Token):
    def validate(self, symbols):
        patterns = []
        patterns += [re.compile(r"^('|`)[^\\]\1$")]
        patterns += [re.compile(r"^('|`)\\[abfnrtv'`\"\\?]\1$")]
        patterns += [re.compile(r"^('|`)\\[0-7]{1, 3}\1$")]
        patterns += [re.compile(r"^('|`)\\x[0-9A-F]+\1$")]
        patterns += [re.compile(r"^('|`)\\u[0-9A-F]{4}\1$")]
        patterns += [re.compile(r"^('|`)\\U[0-9A-F]{8}\1$")]

        for pattern in patterns:
            if pattern.match(symbols):
                break
        else:
            raise CompilerError("Incorrect character constant", self.string)
