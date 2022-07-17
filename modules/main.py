import sys
from lexing.lexer import Lexer
from parsing.parser import Parser
from util.file import generate_map
from util.misc import check_verbose, printv
from util.warnings import CompilerError, Stop

def main():
    options, mode, out_dir, *filenames = sys.argv[1:]
    out_dir = out_dir[:-1] if out_dir[-1] == "/" else out_dir

    check_verbose(options)

    if mode == "t":
        options += "t"

    printv("Finding files and dirs...")
    file_map = generate_map(mode, out_dir, filenames)

    for file_pair in file_map:
        printv(f"Compiling {file_pair[0]}...")
        compile_file(options, file_pair)

def compile_file(options, file_pair):
    try:
        parser = None

        lexer = Lexer(options, file_pair[0])
        lexer.make_tokens()
        print_warnings(lexer)

        parser = Parser(lexer.tokens)
        parser.make_tree()
        print_warnings(parser)

        write_output(file_pair[1])
    except CompilerError as error:
        print(error.printable())
        print_warnings(lexer, throw = False)
        print_warnings(parser, throw = False)
    except Stop:
        pass
    finally:
        output_debug(options, file_pair[0], lexer, parser)

def print_warnings(component, throw = True):
    if component is None:
        return

    for warning in component.warnings:
        print(warning.printable())

    if throw and len(component.warnings) > 0:
        raise Stop

def write_output(out_file_path):
    with open(out_file_path, "w", encoding = "UTF-8") as out_file:
        pass

def output_debug(options, name, lexer, parser):
    if "d" not in options:
        return

    print(f"{name}:")
    print(f"  Tokens:\n    {None if lexer is None else lexer.tokens}")
    print(f"  AST:\n    {None if parser is None else parser.tree}")

if __name__ == "__main__":
    main()
