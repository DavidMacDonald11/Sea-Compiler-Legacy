import sys
from lexing.lexer import Lexer
from lexing.token import Token
from util.file import generate_map
from util.warnings import Warnings

def main():
    options, mode, out_dir, *filenames = sys.argv[1:]
    out_dir = out_dir[:-1] if out_dir[-1] == "/" else out_dir

    if mode == "t":
        options += "t"

    file_map = generate_map(mode, out_dir, filenames)

    for file_pair in file_map:
        compile_file(options, file_pair)

def compile_file(options, file_pair):
    Token.warnings = warnings = Warnings()
    lexer = parser = None

    try:
        lexer = Lexer(warnings, file_pair[0])
        lexer.make_tokens()
        warnings.check()
    except Warnings.CompilerFailure:
        print(warnings)
    finally:
        output_debug(options, file_pair[0], lexer, parser)

def output_debug(options, name, lexer, parser):
    if "d" not in options:
        return

    print(f"{name}:")
    print(f"  Tokens:\n    {None if lexer is None else lexer.tokens}")
    print(f"  Abstract Syntax Tree:\n    {None if parser is None else parser.tree}")

if __name__ == "__main__":
    main()
