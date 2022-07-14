from .token import Token

class Keyword(Token):
    LIST = (
        "alias", "align", "aligned", "alloc", "and", "as", "asm",
        "assert","atomic", "auto", "block", "bool", "break", "bytes",
        "c", "char", "complex", "const", "continue", "dealloc",
        "decorate", "define", "defined", "deviant", "do", "double",
        "else", "enum", "external", "False", "float", "for", "if",
        "in", "is", "imaginary", "include", "Infinity", "inline",
        "int", "local", "long", "manage", "match", "mod","NaN", "not",
        "Null", "of", "or", "pass", "Pi", "real", "realloc", "redefine",
        "register", "restrict", "return","short", "size", "static",
        "str", "struct", "template", "thread", "to", "True", "type",
        "undefine", "union", "void", "volatile", "while", "with", "yield"
    )
