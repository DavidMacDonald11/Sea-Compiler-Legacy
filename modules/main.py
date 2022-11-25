import sys
from lexing.lexer import Lexer
from lexing.token import Token, FakeToken
from parsing.node import Node
from parsing.parser import Parser
from transpiling.transpiler import Transpiler
from util.file import generate_map
from util.warnings import Warnings

def main():
    options, _, out_dir, *filenames = sys.argv[1:]
    out_dir = out_dir[:-1] if out_dir[-1] == "/" else out_dir
    file_map = generate_map(out_dir, filenames)

    for file_pair in file_map:
        compile_file(options, file_pair)

def compile_file(options, file_pair):
    Token.warnings = FakeToken.warnings = warnings = Warnings()
    transpiler = lexer = parser = None

    try:
        lexer = Lexer(warnings, file_pair[0])
        lexer.make_tokens()
        warnings.check()

        Node.parser = parser = Parser(warnings, lexer.tokens)
        parser.make_tree()
        warnings.check()

        Node.c_transpiler = transpiler = Transpiler(warnings, file_pair[1])
        parser.tree.transpile()
        warnings.check()
    except Warnings.CompilerFailure:
        pass
    finally:
        if lexer is not None:
            lexer.close()

        if transpiler is not None:
            transpiler.close()

        output_debug(options, file_pair[0], lexer, parser, transpiler)
        print(warnings)
        sys.exit(len(warnings))

def output_debug(options, name, lexer, parser, transpiler):
    if "d" not in options:
        return

    print(f"{name}:")
    print(f"  Tokens:\n    {None if lexer is None else lexer.tokens}")
    print(f"  Abstract Syntax Tree:\n    {None if parser is None else parser.tree}")
    print(f"  Partial Symbol Table:\n    {None if transpiler is None else transpiler.symbols}\n")

if __name__ == "__main__":
    main()
